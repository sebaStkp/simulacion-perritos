from flask import Flask, jsonify
import time
import random
import threading # Necesario para asegurar que el contador sea thread-safe

app = Flask(__name__)

# --- PARÁMETROS DE UBICACIÓN ---
# 1. PUNTO DE ORIGEN (STATIC) - NO cambia.
LAT_ORIGEN = -17.3950
LON_ORIGEN = -66.1500

# 2. RUTA DE SIMULACIÓN (Puntos en Cochabamba)
# Define una lista de coordenadas por las que la mascota 'caminará'
RUTAS_COCHA = [
    (-17.38195, -66.15995),  # Plaza Colón
    (-17.3895, -66.1568),  # El Prado (sur)
    (-17.396941, -66.158100),  # El Prado (norte)
    (-17.37566, -66.15059),  # Cala Cala
    (-17.3700, -66.1535),  # Recoleta
    # # Cerca del centro
    # (-17.3895, -66.1568), 
    # # Moviéndose al norte (cerca del Prado)
    # (-17.3820, -66.1575), 
    # # Moviéndose al este (cerca del Cristo de la Concordia)
    # (-17.3925, -66.1360), 
    # # Moviéndose de nuevo al centro
    # (-17.3890, -66.1500)  
]

# Variables para controlar el estado del movimiento
indice_actual = 0
lock = threading.Lock() # Bloqueo para manejar el acceso al índice
MOVIMIENTO_MAXIMO = 0.0002 # Reduce el movimiento para centrarlo en el punto de la ruta

# --- FUNCIÓN DE SIMULACIÓN ---
def generar_ubicacion_actual():
    global indice_actual
    
    # Usamos el bloqueo para asegurar que solo una solicitud actualice el índice a la vez
    with lock:
        # 1. Obtiene el punto base (LAT_BASE, LON_BASE) de la ruta
        LAT_BASE, LON_BASE = RUTAS_COCHA[indice_actual]
        
        # 2. Avanza al siguiente punto para la PRÓXIMA solicitud
        # Usamos el operador módulo (%) para volver al inicio cuando se acaba la lista
        indice_actual = (indice_actual + 1) % len(RUTAS_COCHA)

    # 3. Genera la ubicación actual con una pequeña fluctuación sobre el punto base
    delta_lat = random.uniform(-MOVIMIENTO_MAXIMO, MOVIMIENTO_MAXIMO)
    delta_lon = random.uniform(-MOVIMIENTO_MAXIMO, MOVIMIENTO_MAXIMO)
    
    latitud_actual = LAT_BASE + delta_lat
    longitud_actual = LON_BASE + delta_lon
    
    return {
        "latitud": latitud_actual,
        "longitud": longitud_actual,
        "timestamp": time.time(),
        "dispositivo_id": "Mascota-Toby-001" 
    }

# --- ENDPOINT Y EJECUCIÓN ---

@app.route('/ubicacion_mascota', methods=['GET'])
def get_ubicacion_simulada():
    ubicacion_actual = generar_ubicacion_actual()
    
    respuesta = {
        "origin": {
            "latitud": LAT_ORIGEN,
            "longitud": LON_ORIGEN
        },
        "current": ubicacion_actual
    }
    return jsonify(respuesta)

if __name__ == '__main__':
    print("----- SERVIDOR CON MOVIMIENTO SECUENCIAL -----")
    print("La ubicación actual se moverá a través de 4 puntos de Cochabamba con cada solicitud.")
    app.run(host='0.0.0.0', port=5000, debug=True)