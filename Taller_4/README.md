## Taller 4 - API de cálculo de ruta con Docker Swarm

Guía rápida para construir la imagen y desplegar la API Flask en un clúster Docker Swarm.

### Requisitos
- Docker instalado y con soporte para Swarm (`docker swarm init`).
- Puesto 5000 libre en el host.

### 1) Construir la imagen
```bash
docker build -t calculator:1 -f dockerfile .
```

### 2) Inicializar Swarm (solo una vez)
```bash
docker swarm init
```
Si ya tienes un Swarm activo, puedes omitir este paso.

### 3) Desplegar la pila
```bash
docker stack deploy -c docker-compose.yml tsp-stack
```
Esto creará el servicio `api` con 4 réplicas y la red overlay `webnet`.

### 4) Verificar que esté corriendo
```bash
docker service ls
docker service ps tsp-stack_api
```

### 5) Ejecutar el script de fuerza bruta
Con el servicio levantado, ejecuta en tu host:
```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```
```bash
python bruteForce.py
```
El script generará todas las permutaciones de las ciudades, llamará al endpoint `/calculate_distance` de la API y mostrará en consola la mejor ruta y su distancia.

### 6) Detener y limpiar
```bash
docker stack rm tsp-stack
```

### Estructura relevante
- `app.py`: API Flask con el endpoint `/calculate_distance`.
- `dockerfile`: receta de la imagen `calculator:1`.
- `docker-compose.yml`: definición del stack Swarm (servicio, réplicas y red).
