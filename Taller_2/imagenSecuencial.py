import cv2
import numpy as np
import matplotlib.pyplot as plt
import time

# -----------------------------
# 1. Cargar imagen
# -----------------------------
def load_image(path):
    img = cv2.imread(path, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise FileNotFoundError(f"No se pudo cargar la imagen desde: {path}")
    return img

# -----------------------------
# 2. Aplicar Sobel manualmente (secuencial)
# -----------------------------
def sobel_secuencial(img):
    Kx = np.array([[-1, 0, 1],
                   [-2, 0, 2],
                   [-1, 0, 1]], dtype=np.float32)

    Ky = np.array([[-1, -2, -1],
                   [ 0,  0,  0],
                   [ 1,  2,  1]], dtype=np.float32)

    filas, columnas = img.shape
    bordeada = np.zeros_like(img, dtype=np.float32)

    for i in range(1, filas - 1):
        for j in range(1, columnas - 1):
            region = img[i-1:i+2, j-1:j+2]
            Gx = np.sum(Kx * region)
            Gy = np.sum(Ky * region)
            bordeada[i, j] = np.sqrt(Gx**2 + Gy**2)

    bordeada = (bordeada / bordeada.max()) * 255
    return bordeada.astype(np.uint8)

# -----------------------------
# 3. Programa principal
# -----------------------------
if __name__ == "__main__":
    img_path = "C:/Users/ADMIN/TrabajosHPC/Imagenes/brocoli1.png"

    img = load_image(img_path)

    inicio = time.time()
    sobel_img = sobel_secuencial(img)
    fin = time.time()

    tiempo = fin - inicio
    print(f"Tiempo de ejecución (secuencial): {tiempo:.4f} segundos")

    # Crear ventana
    fig = plt.figure(figsize=(10,5))
    manager = plt.get_current_fig_manager()
    manager.set_window_title("Detección de Bordes Sobel (Secuencial)")

    # Imagen original
    plt.subplot(1,2,1)
    plt.imshow(img, cmap='gray')
    plt.title("Imagen Original")
    plt.axis("off")

    # Imagen Sobel con tiempo incrustado
    plt.subplot(1,2,2)
    plt.imshow(sobel_img, cmap='gray')
    plt.title("Sobel Secuencial")
    plt.axis("off")

    # Texto dentro de la imagen
    plt.text(
        0.5, -0.10,  # posición debajo de la imagen
        f"Tiempo de ejecución: {tiempo:.4f} s",
        fontsize=12,
        ha='center',
        transform=plt.gca().transAxes
    )

    plt.tight_layout()
    plt.show()
