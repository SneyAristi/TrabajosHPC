import random
import math
import itertools
import time
import numpy as np
import matplotlib.pyplot as plt
from concurrent.futures import ProcessPoolExecutor, as_completed
from multiprocessing import cpu_count


# === Funciones de utilidad ===
def generar_ciudades(n_ciudades, rango=100):
    """Genera coordenadas aleatorias para las ciudades."""
    return [(random.randint(0, rango), random.randint(0, rango)) for _ in range(n_ciudades)]


def calcular_matriz_distancias(ciudades):
    """Crea una matriz con las distancias euclidianas entre todas las ciudades."""
    n = len(ciudades)
    matriz = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = ciudades[i]
                x2, y2 = ciudades[j]
                matriz[i][j] = math.sqrt((x2 - x1)**2 + (y2 - y1)**2)
    return matriz


def generar_rutas(ciudades):
    """Genera todas las rutas posibles empezando desde la ciudad 0."""
    n = len(ciudades)
    indices = list(range(n))
    ciudad_inicial = indices[0]
    otras_ciudades = indices[1:]
    rutas = []
    for perm in itertools.permutations(otras_ciudades):
        ruta = [ciudad_inicial] + list(perm) + [ciudad_inicial]
        rutas.append(ruta)
    return rutas


def calcular_distancia_total(ruta, matriz):
    """Calcula la distancia total de una ruta."""
    distancia = 0
    for i in range(len(ruta) - 1):
        distancia += matriz[ruta[i]][ruta[i + 1]]
    return distancia


# === SECUENCIAL ===
def viajero_secuencial(matriz, rutas):
    inicio = time.perf_counter()
    mejor_ruta = None
    menor_distancia = float('inf')

    for ruta in rutas:
        distancia = calcular_distancia_total(ruta, matriz)
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_ruta = ruta

    fin = time.perf_counter()
    tiempo = fin - inicio

    print("\n🧭 [Secuencial]")
    print("Mejor ruta:", mejor_ruta)
    print("Distancia mínima:", round(menor_distancia, 2))
    print(f"Tiempo de ejecución: {tiempo:.6f} segundos")

    return mejor_ruta, menor_distancia, tiempo


# === PARALELO CON ProcessPoolExecutor ===
def procesar_rutas(sub_rutas, matriz):
    """Función auxiliar que busca la mejor ruta dentro de un subconjunto."""
    mejor = None
    menor = float('inf')
    for ruta in sub_rutas:
        d = calcular_distancia_total(ruta, matriz)
        if d < menor:
            menor = d
            mejor = ruta
    return mejor, menor


def viajero_paralelo(matriz, rutas, n_processes):
    inicio = time.perf_counter()

    # Dividir rutas en partes para cada proceso
    chunk_size = len(rutas) // n_processes
    subsets = [rutas[i:i + chunk_size] for i in range(0, len(rutas), chunk_size)]

    mejor_global = None
    menor_global = float('inf')

    with ProcessPoolExecutor(max_workers=n_processes) as executor:
        futures = [executor.submit(procesar_rutas, subset, matriz) for subset in subsets]
        for future in as_completed(futures):
            mejor_local, menor_local = future.result()
            if menor_local < menor_global:
                menor_global = menor_local
                mejor_global = mejor_local

    fin = time.perf_counter()
    tiempo = fin - inicio

    print("\n⚙️ [Paralelo - ProcessPoolExecutor]")
    print("Mejor ruta:", mejor_global)
    print("Distancia mínima:", round(menor_global, 2))
    print(f"Tiempo de ejecución: {tiempo:.6f} segundos")

    return mejor_global, menor_global, tiempo


# === GRAFICAR ===
def graficar_ruta(ciudades, ruta, titulo, tiempo):
    x = [ciudades[i][0] for i in ruta]
    y = [ciudades[i][1] for i in ruta]

    plt.figure(figsize=(6, 6))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    for i, (cx, cy) in enumerate(ciudades):
        plt.text(cx + 1, cy + 1, str(i + 1), fontsize=8, color='red')

    plt.title(f"{titulo}\nTiempo: {tiempo:.4f} s")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(True)
    plt.show()


# === MAIN ===
def main():
    print("=== PROBLEMA DEL VIAJERO (TSP) ===")
    n = int(input("Ingrese el número de ciudades (≤10 recomendado): "))
    n_processes = min(4, cpu_count())

    ciudades = generar_ciudades(n)
    matriz = calcular_matriz_distancias(ciudades)
    rutas = generar_rutas(ciudades)

    # Secuencial
    mejor_ruta_seq, dist_seq, t_seq = viajero_secuencial(matriz, rutas)

    # Paralelo
    mejor_ruta_par, dist_par, t_par = viajero_paralelo(matriz, rutas, n_processes)

    # Graficar
    graficar_ruta(ciudades, mejor_ruta_seq, "Ruta Óptima - Secuencial", t_seq)
    graficar_ruta(ciudades, mejor_ruta_par, "Ruta Óptima - Paralelo", t_par)

    print("\n📊 Comparación final:")
    print(f"Tiempo Secuencial: {t_seq:.4f} s")
    print(f"Tiempo Paralelo ({n_processes} procesos): {t_par:.4f} s")
    print(f"Aceleración: {t_seq / t_par:.2f}x")


if __name__ == "__main__":
    main()
