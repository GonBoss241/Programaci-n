# app.py
from flask import Flask, render_template, request, redirect, url_for, session, flash

# 1. INICIALIZACIÓN DE FLASK
app = Flask(__name__)
# Se necesita una 'secret_key' para que Flask gestione datos de sesión de forma segura.
app.secret_key = 'una-clave-secreta-muy-segura' 

# --- LÓGICA DEL NEGOCIO (Adaptada de tu código original) ---

COSTO_ESTACIONAMIENTO_CENTAVOS = 400  # $4.00

# Opciones de pago que el usuario puede insertar
PAGOS_ACEPTADOS = [
    {"valor": 50, "nombre": "una moneda de 50 centavos"},
    {"valor": 100, "nombre": "una moneda de $1"},
    {"valor": 500, "nombre": "un billete de $5"},
    {"valor": 1000, "nombre": "un billete de $10"},
    {"valor": 2000, "nombre": "un billete de $20"}
]

def calcular_cambio_optimo(pago_total_centavos, costo_centavos):
    """
    Calcula el cambio óptimo a devolver.
    Devuelve una lista de strings con el cambio desglosado.
    """
    if pago_total_centavos <= costo_centavos:
        return None, [] # No hay cambio a devolver

    cambio_total_centavos = pago_total_centavos - costo_centavos
    cambio_restante_centavos = cambio_total_centavos
    
    cambio_desglosado = []

    cambio_disponible = [
        {"valor": 10000, "singular": "billete de $100", "plural": "billetes de $100"},
        {"valor": 5000, "singular": "billete de $50", "plural": "billetes de $50"},
        {"valor": 2000, "singular": "billete de $20", "plural": "billetes de $20"},
        {"valor": 1000, "singular": "billete de $10", "plural": "billetes de $10"},
        {"valor": 500, "singular": "billete de $5", "plural": "billetes de $5"},
        {"valor": 100, "singular": "moneda de $1", "plural": "monedas de $1"},
        {"valor": 50, "singular": "moneda de 50 centavos", "plural": "monedas de 50 centavos"}
    ]

    for denom in cambio_disponible:
        valor_denom = denom["valor"]
        if cambio_restante_centavos >= valor_denom:
            cantidad = cambio_restante_centavos // valor_denom
            cambio_restante_centavos %= valor_denom
            nombre = denom["singular"] if cantidad == 1 else denom["plural"]
            cambio_desglosado.append(f"{cantidad} {nombre}")

    return cambio_total_centavos / 100.0, cambio_desglosado

# 2. DEFINICIÓN DE RUTAS (Las "páginas" de nuestro sitio web)

@app.route('/')
def inicio():
    """
    Esta función se ejecuta cuando alguien visita la página principal.
    Inicializa el pago acumulado en la sesión del usuario.
    """
    session['pago_acumulado_centavos'] = 0
    return redirect(url_for('estacionamiento'))

@app.route('/estacionamiento')
def estacionamiento():
    """
    Muestra la página principal de pago del estacionamiento.
    """
    pago_acumulado_centavos = session.get('pago_acumulado_centavos', 0)

    # Si ya se pagó lo suficiente, calculamos el cambio
    if pago_acumulado_centavos >= COSTO_ESTACIONAMIENTO_CENTAVOS:
        cambio_total, cambio_desglosado = calcular_cambio_optimo(
            pago_acumulado_centavos, COSTO_ESTACIONAMIENTO_CENTAVOS
        )
        return render_template('index.html', 
                               pago_completado=True,
                               cambio_total=cambio_total,
                               cambio_desglosado=cambio_desglosado,
                               pago_total=pago_acumulado_centavos / 100.0,
                               costo_total=COSTO_ESTACIONAMIENTO_CENTAVOS / 100.0)

    # Si aún no se ha pagado, mostramos la interfaz de pago
    return render_template('index.html', 
                           costo_total=COSTO_ESTACIONAMIENTO_CENTAVOS / 100.0,
                           pago_acumulado=pago_acumulado_centavos / 100.0,
                           restante=(COSTO_ESTACIONAMIENTO_CENTAVOS - pago_acumulado_centavos) / 100.0,
                           pagos_aceptados=PAGOS_ACEPTADOS,
                           pago_completado=False)

@app.route('/pagar', methods=['POST'])
def pagar():
    """
    Esta función procesa el pago enviado desde el formulario HTML.
    """
    try:
        # Obtenemos el valor del botón que el usuario presionó
        pago_insertado_valor = int(request.form['pago'])
        
        # Actualizamos el total pagado en la sesión del usuario
        session['pago_acumulado_centavos'] = session.get('pago_acumulado_centavos', 0) + pago_insertado_valor
        
        # Usamos flash para mostrar un mensaje de confirmación
        pago_info = next((p for p in PAGOS_ACEPTADOS if p['valor'] == pago_insertado_valor), None)
        if pago_info:
            flash(f"Ha insertado {pago_info['nombre']}.", 'success')

    except (KeyError, ValueError):
        flash("Error al procesar el pago. Inténtelo de nuevo.", 'error')

    # Redirigimos al usuario de vuelta a la página de estacionamiento para que vea el estado actualizado
    return redirect(url_for('estacionamiento'))

# --- Punto de entrada para ejecutar la aplicación ---
if __name__ == '__main__':
    # debug=True hace que el servidor se reinicie automáticamente con cada cambio.
    # ¡No uses debug=True en un entorno de producción!
    app.run(debug=True)