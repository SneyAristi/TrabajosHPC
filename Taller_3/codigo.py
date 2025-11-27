import cv2, os, time, zipfile
from concurrent.futures import ThreadPoolExecutor, as_completed

# 1. CONFIGURACIÓN
video_path = "animacion con plastilina.mp4"
workdir = "taller_output"
frames_dir = f"{workdir}/frames_originales"
seq_dir = f"{workdir}/frames_gris_secuencial"
par_dir = f"{workdir}/frames_gris_paralelo"
os.makedirs(frames_dir, exist_ok=True)
os.makedirs(seq_dir, exist_ok=True)
os.makedirs(par_dir, exist_ok=True)

# 2. LECTURA DEL VIDEO
cap = cv2.VideoCapture(video_path)
if not cap.isOpened():
    raise Exception("No se pudo abrir el video.")

frame_count = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
fps = cap.get(cv2.CAP_PROP_FPS) or 30
w = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
h = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

print("Frames:", frame_count, "FPS:", fps)

# 3. EXTRAER FRAMES
frames = []
i = 0
while True:
    ret, frame = cap.read()
    if not ret:
        break
    fname = f"frame_{i:05d}.jpg"
    cv2.imwrite(f"{frames_dir}/{fname}", frame)
    frames.append(fname)
    i += 1
cap.release()

print("Extracción lista:", len(frames), "frames")

# 4. FUNCIÓN DE CONVERSIÓN
def convertir(path_in, folder_out):
    img = cv2.imread(path_in)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    cv2.imwrite(f"{folder_out}/{os.path.basename(path_in)}", gray)

# 5. SECUENCIAL
t0 = time.time()
for fname in frames:
    convertir(f"{frames_dir}/{fname}", seq_dir)
t1 = time.time()
t_seq = t1 - t0
print("Tiempo SECUENCIAL:", t_seq)

# 6. PARALELO
t0 = time.time()
with ThreadPoolExecutor() as ex:
    tasks = [ex.submit(convertir, f"{frames_dir}/{fname}", par_dir) for fname in frames]
    for t in as_completed(tasks):
        _ = t.result()
t1 = time.time()
t_par = t1 - t0
print("Tiempo PARALELO:", t_par)

speedup = t_seq / t_par
print("SPEEDUP:", speedup)

# 7. RECONSTRUIR VIDEOS
fourcc = cv2.VideoWriter_fourcc(*'mp4v')

def build_video(in_folder, out_name):
    out = cv2.VideoWriter(out_name, fourcc, fps, (w, h), isColor=False)
    files = sorted(os.listdir(in_folder))
    for f in files:
        img = cv2.imread(f"{in_folder}/{f}", cv2.IMREAD_GRAYSCALE)
        out.write(img)
    out.release()

build_video(seq_dir, f"{workdir}/video_gris_secuencial.mp4")
build_video(par_dir, f"{workdir}/video_gris_paralelo.mp4")
print("Videos reconstruidos.")

# 8. CREAR ZIP
zip_path = "entrega_taller_video_gris.zip"

with zipfile.ZipFile(zip_path, "w") as z:
    for folder, _, files in os.walk(workdir):
        for f in files:
            full = os.path.join(folder, f)
            arc = os.path.relpath(full, workdir)
            z.write(full, arc)

with zipfile.ZipFile(zip_path, "a") as z:
    z.write(video_path, os.path.basename(video_path))

print("ZIP creado:", zip_path)
