import csv
import itertools
import logging
import os
import random
import time
from pathlib import Path
import aiohttp
import asyncio

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s",
)

CALCULATOR_URL = os.environ.get(
    "CALCULATOR_URL",
    "http://localhost:5000/calculate_distance",
)
SECUENCIAL = 0
NUM_CITIES = 9
METRICS_CSV = Path("metrics_cluster.csv")
NUMBER_OF_RUNS = 1

# =========================================
# 1. Datos de Entrada: Lista de Ciudades
# =========================================
def generate_random_cities(num_cities):
    """
    Genera num_cities ciudades con coordenadas aleatorias en el plano [0,100]x[0,100].
    """
    rng = random.Random()
    cities_local = []
    for idx in range(num_cities):
        city_id = f"C{idx + 1}"
        cities_local.append(
            {
                "id": city_id,
                "x": rng.uniform(0, 100),
                "y": rng.uniform(0, 100),
            }
        )
    return cities_local

# =========================================
# 2. Generación de Rutas: Permutaciones de Ciudades
# =========================================
def generate_paths(cities):
    """
    Crea todas las permutaciones posibles de ciudades y las devuelve como un iterable.
    """
    city_ids = [city["id"] for city in cities]
    return itertools.permutations(city_ids)

# =========================================
# 3. Cálculo de Distancia Asíncrono: Solicitud a la API
# =========================================
async def calculate_distance(session, path, city_map):
    """
    Función asíncrona para calcular la distancia de una ruta utilizando una solicitud HTTP.
    """
    payload = {"cities": []}

    for city_id in path:
        city_data = city_map.get(city_id)

        if city_data:
            payload["cities"].append(
                {
                    "id": city_id,
                    "x": city_data["x"],
                    "y": city_data["y"],
                }
            )
        else:
            raise ValueError(f"Ciudad con id {city_id} no encontrada.")

    # Realiza la solicitud POST de manera asíncrona
    async with session.post(CALCULATOR_URL, json=payload) as response:
        if response.status == 200:
            result = await response.json()
            return result["total_distance"]
        response.raise_for_status()

# =========================================
# 4. Función para Grabar Métricas en CSV
# =========================================
def append_metrics_row(row):
    """
    Registra métricas en un archivo CSV, creando el archivo si no existe.
    """
    METRICS_CSV.parent.mkdir(parents=True, exist_ok=True)
    fieldnames = [
        "num_cities",
        "paths_processed",
        "best_distance",
        "duration_s",
    ]
    exists = METRICS_CSV.exists()
    with METRICS_CSV.open("a", newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if not exists:
            writer.writeheader()
        writer.writerow(row)

# =========================================
# 5. Optimización de la Ruta: Encontrar la Mejor Ruta
# =========================================
async def find_best_path(cities):
    """
    Función asíncrona que encuentra la mejor ruta entre las ciudades utilizando múltiples tareas en paralelo.
    """
    best_path = None
    best_distance = float('inf')  # Inicializamos con una distancia infinita
    total_paths = 0
    started = time.perf_counter()

    # Generamos las rutas (permutaciones)
    paths = generate_paths(cities)
    city_map = {city["id"]: city for city in cities}

    # Inicia una sesión asíncrona para las solicitudes HTTP
    async with aiohttp.ClientSession() as session:
        tasks = []
        for path in paths:
            # Para cada ruta, creamos una tarea asíncrona para calcular la distancia
            tasks.append(calculate_distance(session, path, city_map))

        # Ejecutamos todas las tareas en paralelo y esperamos los resultados
        distances = await asyncio.gather(*tasks)

        # Procesamos los resultados de las distancias
        for i, distance in enumerate(distances):
            if distance < best_distance:
                best_distance = distance
                best_path = list(itertools.islice(generate_paths(cities), i, i+1))[0]  # Obtener el path correspondiente

            total_paths += 1

    elapsed = time.perf_counter() - started
    if best_path:
        logging.info("La mejor ruta es: %s", " -> ".join(best_path))
        logging.info("Con una distancia total de: %.4f unidades", best_distance)
        logging.info("Tiempo: %.4f", elapsed)
    else:
        logging.error("No se pudo encontrar una ruta válida.")

    append_metrics_row(
        {
            "num_cities": len(cities),
            "paths_processed": total_paths,
            "best_distance": best_distance if best_path else "",
            "duration_s": round(elapsed, 4),
        }
    )

# =========================================
# 6. Ejecutar la Búsqueda de la Mejor Ruta
# =========================================
if __name__ == "__main__":
    if SECUENCIAL:
        for i in range(2, NUM_CITIES + 1):
            for _ in range(NUMBER_OF_RUNS):
                cities = generate_random_cities(i)
                # Ejecutamos la búsqueda de la mejor ruta de forma secuencial
                asyncio.run(find_best_path(cities))
    else:
        for _ in range(NUMBER_OF_RUNS):
            cities = generate_random_cities(NUM_CITIES)
            # Ejecutamos la búsqueda de la mejor ruta de forma asíncrona
            asyncio.run(find_best_path(cities))
