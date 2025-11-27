import itertools
import requests
# =========================================
# 1. Datos de Entrada: Lista de Ciudades
# =========================================
cities = [
    { "id": "A", "x": 0.0, "y": 0.0 },
    { "id": "B", "x": 3.0, "y": 4.0 },
    { "id": "C", "x": 30.0, "y": 8.0 },
    { "id": "D", "x": 9.0, "y": 12.0 },
    { "id": "E", "x": 12.0, "y": 16.0 },
    { "id": "F", "x": 15.0, "y": 20.0 }
]

# =========================================
# 2. Generación de Rutas: Permutaciones de Ciudades
# =========================================
def generate_paths(cities):
    """
    Función que genera todas las posibles permutaciones de las ciudades.

    Parametros:
    cities (list): Lista de diccionarios con los identificadores de ciudades y sus coordenadas.

    Retorno:
    list: Lista con todas las permutaciones posibles de los identificadores de las ciudades.
    """
    # Crear una lista solo con los ids de las ciudades
    city_ids = [city["id"] for city in cities]
    # Generar todas las permutaciones posibles
    return list(itertools.permutations(city_ids))

# =========================================
# 3. Cálculo de Distancia: Solicitud a la API
# =========================================
def calculate_distance(path):
    """
    Función que calcula la distancia total de una ruta utilizando la API Flask.

    Parametros:
    path (tuple): Tupla con el orden de los identificadores de las ciudades a visitar.

    Retorno:
    float: Distancia total de la ruta calculada por la API.
    """
    # Definir la URL del servicio RESTful de la API de Flask que calcula la distancia
    url = "http://localhost:5000/calculate_distance"  # Ajustar según el servicio en Docker Swarm

    # Preparar el cuerpo de la solicitud (JSON)
    payload = {
        "cities": []
    }

    for city_id in path:
        # Buscar las coordenadas de la ciudad correspondiente a city_id
        city_data = next((city for city in cities if city["id"] == city_id), None)
        
        if city_data:
            payload["cities"].append({
                "id": city_id,
                "x": city_data["x"],
                "y": city_data["y"]
            })
        else:
            print(f"Error: Ciudad con id {city_id} no encontrada.")
            return None

    # Hacer la solicitud POST a la API para obtener la distancia total
    response = requests.post(url, json=payload)
    
    if response.status_code == 200:
        # Si la respuesta es exitosa, devolver la distancia total
        return response.json()["total_distance"]
    else:
        # Si algo falla, retornar None
        print(f"Error en la solicitud: {response.status_code}")
        return None


# =========================================
# 4. Optimización de la Ruta: Encontrar la Mejor Ruta
# =========================================
def find_best_path():
    """
    Función que encuentra la mejor ruta (la ruta más corta) entre todas las permutaciones de las ciudades.

    Este proceso genera todas las permutaciones posibles de las ciudades, calcula la distancia de cada ruta
    usando la función `calculate_distance`, y mantiene un registro de la mejor ruta encontrada.

    Retorno:
    None: Imprime la mejor ruta y su distancia en consola.
    """
    # Generar todas las permutaciones posibles de las ciudades
    paths = generate_paths(cities)
    # Inicializar variables para almacenar la mejor ruta y su distancia
    best_path = None
    best_distance = float('inf')  # Iniciar con una distancia infinita
    
    # Iterar sobre cada ruta generada
    for path in paths:
        # Calcular la distancia de la ruta actual
        distance = calculate_distance(path)
        
        if distance is not None and distance < best_distance:
            # Si la distancia calculada es mejor que la mejor encontrada hasta ahora
            best_distance = distance
            best_path = path
    
    # Imprimir el resultado final
    if best_path:
        print(f"La mejor ruta es: {' -> '.join(best_path)}")
        print(f"Con una distancia total de: {best_distance} unidades")
    else:
        print("No se pudo encontrar una ruta válida.")

# =========================================
# 5. Ejecutar la Búsqueda de la Mejor Ruta
# =========================================
if __name__ == "__main__":
    find_best_path()
