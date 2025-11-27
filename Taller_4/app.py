"""
====================================================
 API REST para cálculo de distancia de rutas (TSP)
 Taller Práctico 4 - HPC / Microservicios
====================================================

Este servicio expone un endpoint POST /calculate_distance
que recibe una lista ordenada de ciudades con coordenadas
cartesianas y devuelve la distancia total recorrida
(usando distancia euclidiana entre puntos consecutivos).
"""
from flask import Flask, request, jsonify
import math

# Inicialización de la aplicación
app = Flask(__name__)


# =========================================
# 1. Funciones auxiliares de cálculo
# =========================================
def euclidean_distance(point_a, point_b):
    """
    Calcula la distancia euclidiana entre dos puntos 2D.

    Parameters
    ----------
    point_a : dict
        Diccionario con las llaves "x" y "y" (float).
    point_b : dict
        Diccionario con las llaves "x" y "y" (float).

    Returns
    -------
    float
        Distancia euclidiana entre point_a y point_b.
    """
    dx = point_b["x"] - point_a["x"]
    dy = point_b["y"] - point_a["y"]
    return math.sqrt(dx * dx + dy * dy)


def total_route_distance(cities):
    """
    Suma las distancias euclidianas entre cada par consecutivo
    de ciudades en la lista.

    Parameters
    ----------
    cities : list[dict]
        Lista de ciudades en el orden a visitar. Cada elemento
        debe tener al menos las llaves "x" y "y".

    Returns
    -------
    float
        Distancia total recorrida siguiendo el orden de la lista.
    """
    if len(cities) < 2:
        # Si hay 0 o 1 ciudad, la distancia recorrida es 0
        return 0.0

    total = 0.0
    # Recorremos pares consecutivos: (ciudad[i], ciudad[i+1])
    for i in range(len(cities) - 1):
        total += euclidean_distance(cities[i], cities[i + 1])

    return total


# =========================================
# 4. Endpoint principal: /calculate_distance
# =========================================
@app.route("/calculate_distance", methods=["POST"])
def calculate_distance():
    """
    Endpoint que recibe un JSON con la lista de ciudades
    y retorna la distancia total de la ruta.

    Formato esperado del cuerpo (JSON):
    {
        "cities": [
            { "id": "A", "x": 0.0, "y": 0.0 },
            { "id": "B", "x": 3.0, "y": 4.0 },
            ...
        ]
    }

    Respuesta (JSON):
    {
        "total_distance": <float>
    }
    """
    # -----------------------------
    # 4.1. Validación de la entrada
    # -----------------------------
    data = request.get_json()

    if not data:
        return jsonify({"error": "JSON body is required"}), 400

    if "cities" not in data:
        return jsonify({"error": "Field 'cities' is required"}), 400

    cities = data["cities"]

    if not isinstance(cities, list) or len(cities) == 0:
        return jsonify({"error": "'cities' must be a non-empty list"}), 400

    # Validamos que cada ciudad tenga x e y numéricos
    for idx, city in enumerate(cities):
        if not isinstance(city, dict):
            return jsonify({"error": f"City at index {idx} must be an object"}), 400

        if "x" not in city or "y" not in city:
            return jsonify({"error": f"City at index {idx} must have 'x' and 'y'"}), 400

        try:
            city["x"] = float(city["x"])
            city["y"] = float(city["y"])
        except (ValueError, TypeError):
            return jsonify({"error": f"'x' and 'y' for city at index {idx} must be numeric"}), 400

    # -----------------------------
    # 4.2. Cálculo de la distancia
    # -----------------------------
    total = total_route_distance(cities)

    # -----------------------------
    # 4.3. Respuesta al cliente
    # -----------------------------
    return jsonify({"total_distance": total}), 200

# =========================================
# Endpoint de healthcheck
# =========================================
@app.route("/", methods=["GET"])
def healthcheck():
    """
    Endpoint de healthcheck para verificar si la API está funcionando correctamente.
    """
    return jsonify({"status": "ok"}), 200

# =========================================
# 5. Punto de entrada para ejecución local
# =========================================
if __name__ == "__main__":
    # host="0.0.0.0" para que funcione dentro de contenedores Docker
    # y sea accesible desde fuera del contenedor.
    app.run(host='0.0.0.0', port=5000)
