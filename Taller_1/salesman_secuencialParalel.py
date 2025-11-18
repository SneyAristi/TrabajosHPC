import random
import math
import itertools
import time
import os
import matplotlib.pyplot as plt
from multiprocessing import Pool, cpu_count

# ==========================
# FUNCIONES AUXILIARES
# ==========================

def generar_ciudades(n_ciudades, rango=100):
    """Genera una lista de ciudades con coordenadas (x, y) aleatorias."""
    return [(random.randint(0, rango), random.randint(0, rango)) for _ in range(n_ciudades)]


def calcular_matriz_distancias(ciudades):
    """Crea una matriz de distancias euclidianas entre todas las ciudades."""
    n = len(ciudades)
    matriz = [[0.0 for _ in range(n)] for _ in range(n)]
    for i in range(n):
        for j in range(n):
            if i != j:
                x1, y1 = ciudades[i]
                x2, y2 = ciudades[j]
                matriz[i][j] = math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)
    return matriz


def graficar_ciudades(ciudades):
    """Grafica las ciudades generadas en un plano cartesiano."""
    x = [c[0] for c in ciudades]
    y = [c[1] for c in ciudades]
    plt.figure(figsize=(6, 6))
    plt.scatter(x, y, c='blue', marker='o')
    for i, (cx, cy) in enumerate(ciudades):
        plt.text(cx + 1, cy + 1, str(i + 1), fontsize=9, color='red')
    plt.title("Distribución de Ciudades (Problema del Viajero)")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(True)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.show()


def graficar_ruta(ciudades, ruta, tiempo, tipo="Secuencial"):
    """Grafica la mejor ruta encontrada."""
    plt.figure(figsize=(6, 6))
    x = [ciudades[i][0] for i in ruta]
    y = [ciudades[i][1] for i in ruta]
    plt.plot(x, y, '-o', color='green')
    for i, (cx, cy) in enumerate(ciudades):
        plt.text(cx + 1, cy + 1, str(i + 1), fontsize=9, color='red')
    plt.title(f"Mejor Ruta ({tipo}) - Tiempo: {tiempo:.4f}s")
    plt.xlabel("Coordenada X")
    plt.ylabel("Coordenada Y")
    plt.grid(True)
    plt.xlim(0, 100)
    plt.ylim(0, 100)
    plt.show()


# ==========================
# CÁLCULOS DE DISTANCIA Y RUTAS
# ==========================

def generar_rutas(ciudades):
    """Genera todas las rutas posibles empezando desde la ciudad 0."""
    n = len(ciudades)
    indices = list(range(n))
    ciudad_inicial = indices[0]
    otras_ciudades = indices[1:]
    rutas = [[ciudad_inicial] + list(perm) + [ciudad_inicial] for perm in itertools.permutations(otras_ciudades)]
    return rutas


def calcular_distancia_total(ruta, matriz):
    """Calcula la distancia total de una ruta."""
    return sum(matriz[ruta[i]][ruta[i + 1]] for i in range(len(ruta) - 1))


# ==========================
# VERSIÓN SECUENCIAL
# ==========================

def secuencial_viajero(matriz, rutas):
    inicio = time.perf_counter()
    mejor_ruta = None
    menor_distancia = float('inf')

    for ruta in rutas:
        distancia = calcular_distancia_total(ruta, matriz)
        if distancia < menor_distancia:
            menor_distancia = distancia
            mejor_ruta = ruta

    fin = time.perf_counter()
    tiempo_total = fin - inicio

    print("🧭 Mejor ruta (Secuencial):", mejor_ruta)
    print("Distancia mínima:", round(menor_distancia, 2))
    print(f"⏱ Tiempo secuencial: {tiempo_total:.4f} segundos\n")

    return mejor_ruta, menor_distancia, tiempo_total


# ==========================
# VERSIÓN PARALELA (Pool)
# ==========================

def _worker_ruta(ruta_matriz):
    """Función auxiliar para evaluar una ruta (para usar con Pool)."""
    ruta, matriz = ruta_matriz
    return calcular_distancia_total(ruta, matriz)


def paralelo_viajero(matriz, rutas, n_processes):
    inicio = time.perf_counter()

    # Preparamos las rutas junto con la matriz (para evitar variables globales)
    datos = [(ruta, matriz) for ruta in rutas]

    with Pool(processes=n_processes) as pool:
        distancias = pool.map(_worker_ruta, datos)

    # Encontrar la mejor ruta
    menor_distancia = min(distancias)
    mejor_ruta = rutas[distancias.index(menor_distancia)]

    fin = time.perf_counter()
    tiempo_total = fin - inicio

    print("🧭 Mejor ruta (Paralelo):", mejor_ruta)
    print("Distancia mínima:", round(menor_distancia, 2))
    print(f"⏱ Tiempo paralelo ({n_processes} procesos): {tiempo_total:.4f} segundos\n")

    return mejor_ruta, menor_distancia, tiempo_total


# ==========================
# FUNCIÓN PRINCIPAL
# ==========================

def main():
    print("=== PROBLEMA DEL VIAJERO (Comparación Secuencial vs Paralelo) ===\n")
    n = int(input("Ingrese el número de ciudades: "))

    ciudades = generar_ciudades(n)
    graficar_ciudades(ciudades)
    matriz = calcular_matriz_distancias(ciudades)
    rutas = generar_rutas(ciudades)

    # Número de procesos
    n_processes = min(6, cpu_count())  # máximo 4 o núcleos disponibles

    # Ejecuciones
    print("🚀 Ejecutando versión secuencial...")
    mejor_ruta_seq, menor_dist_seq, tiempo_seq = secuencial_viajero(matriz, rutas)

    print("🚀 Ejecutando versión paralela...")
    mejor_ruta_par, menor_dist_par, tiempo_par = paralelo_viajero(matriz, rutas, n_processes)

    # Comparación final
    print("📊 Comparación final:")
    print(f"Secuencial: {tiempo_seq:.4f} s")
    print(f"Paralelo ({n_processes} procesos): {tiempo_par:.4f} s")
    print(f"Aceleración: {tiempo_seq / tiempo_par:.2f}x\n")

    # Graficar rutas
    graficar_ruta(ciudades, mejor_ruta_seq, tiempo_seq, tipo="Secuencial")
    graficar_ruta(ciudades, mejor_ruta_par, tiempo_par, tipo="Paralelo")


# ==========================
# EJECUCIÓN
# ==========================
if __name__ == "__main__":
    main()
