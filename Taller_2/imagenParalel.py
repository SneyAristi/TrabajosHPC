import cv2
import numpy as np
import time
from multiprocessing import Pool, cpu_count
import matplotlib.pyplot as plt

# ==========================
# FUNCIONES AUXILIARES
# ==========================

def load_image(path):
    """Carga una imagen en escala de grises."""
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen desde: {path}")
    return img


def sobel_worker(args):
    """Función que aplica Sobel a un bloque de la imagen (para usar en paralelo)."""
    bloque, Kx, Ky = args
    filas, columnas = bloque.shape
    bloque_resultado = np.zeros_like(bloque, dtype=np.float32)

    # Aplicar convolución 3x3 (idéntico al secuencial)
    for i in range(1, filas - 1):
        for j in range(1, columnas - 1):
            region = bloque[i - 1:i + 2, j - 1:j + 2]
            Gx = np.sum(Kx * region)
            Gy = np.sum(Ky * region)
            bloque_resultado[i, j] = np.sqrt(Gx ** 2 + Gy ** 2)

    return bloque_resultado


def sobel_paralelo(img, n_processes=None):
    """Aplica el filtro Sobel en paralelo dividiendo la imagen en bloques horizontales."""
    if n_processes is None:
        n_processes = min(4, cpu_count())

    # Kernels Sobel
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)
    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float32)

    # Dividir imagen en bloques (con solapamiento de 1 fila)
    filas, columnas = img.shape
    paso = filas // n_processes
    bloques = []

    for i in range(n_processes):
        inicio = i * paso
        fin = (i + 1) * paso if i < n_processes - 1 else filas
        bloque = img[max(0, inicio - 1):min(filas, fin + 1), :]  # margen para el borde
        bloques.append((bloque, Kx, Ky))

    # Procesar en paralelo
    inicio_tiempo = time.perf_counter()

    with Pool(processes=n_processes) as pool:
        resultados = pool.map(sobel_worker, bloques)

    fin_tiempo = time.perf_counter()

    # Reconstruir la imagen final
    resultado_final = np.zeros_like(img, dtype=np.float32)
    inicio_actual = 0
    for i, bloque_resultado in enumerate(resultados):
        # Cortar las filas solapadas
        if i == 0:
            bloque_sin_borde = bloque_resultado[:-1, :]
        elif i == n_processes - 1:
            bloque_sin_borde = bloque_resultado[1:, :]
        else:
            bloque_sin_borde = bloque_resultado[1:-1, :]

        fin_actual = inicio_actual + bloque_sin_borde.shape[0]
        resultado_final[inicio_actual:fin_actual, :] = bloque_sin_borde
        inicio_actual = fin_actual

    # Normalizar
    resultado_final = (resultado_final / resultado_final.max()) * 255
    resultado_final = resultado_final.astype(np.uint8)

    tiempo_total = fin_tiempo - inicio_tiempo
    return resultado_final, tiempo_total


# ==========================
# PROGRAMA PRINCIPAL
# ==========================

if __name__ == "__main__":
    img_path = "C:/Users/ADMIN/TrabajosHPC/Imagenes/brocoli1.png"  # cambia a tu imagen

    img = load_image(img_path)

    print("🚀 Ejecutando Sobel en paralelo...")
    sobel_img, tiempo_par = sobel_paralelo(img, n_processes=4)
    print(f"⏱ Tiempo paralelo (4 procesos): {tiempo_par:.4f} segundos")

    # Visualizar resultado
    plt.figure(figsize=(10, 5))
    plt.subplot(1, 2, 1)
    plt.imshow(img, cmap='gray')
    plt.title("Imagen Original")
    plt.axis('off')

    plt.subplot(1, 2, 2)
    plt.imshow(sobel_img, cmap='gray')
    plt.title(f"Sobel Paralelo ({tiempo_par:.4f}s)")
    plt.axis('off')

    plt.tight_layout()
    plt.show()
