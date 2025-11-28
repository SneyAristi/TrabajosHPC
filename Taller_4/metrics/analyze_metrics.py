import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean
from typing import Dict, List, Tuple

import matplotlib.pyplot as plt


def load_metrics(path: Path) -> List[dict]:
    with path.open() as f:
        reader = csv.DictReader(f)
        return [
            {
                "num_cities": int(row["num_cities"]),
                "paths_processed": int(row["paths_processed"]),
                "best_distance": float(row["best_distance"]),
                "duration_s": float(row["duration_s"]),
            }
            for row in reader
        ]


def avg_by_city(rows: List[dict]) -> Dict[int, dict]:
    grouped: Dict[int, defaultdict] = defaultdict(lambda: defaultdict(list))
    for row in rows:
        n = row["num_cities"]
        for key in ("paths_processed", "best_distance", "duration_s"):
            grouped[n][key].append(row[key])
    return {
        n: {metric: mean(values) for metric, values in metrics.items()}
        for n, metrics in grouped.items()
    }


def build_series(
    local_avg: Dict[int, dict], swarm_avg: Dict[int, dict]
) -> Tuple[List[int], List[float], List[float], List[float], List[float]]:
    cities = sorted(set(local_avg) | set(swarm_avg))
    local_duration = [local_avg.get(n, {}).get("duration_s", 0.0) for n in cities]
    swarm_duration = [swarm_avg.get(n, {}).get("duration_s", 0.0) for n in cities]
    local_distance = [local_avg.get(n, {}).get("best_distance", 0.0) for n in cities]
    swarm_distance = [swarm_avg.get(n, {}).get("best_distance", 0.0) for n in cities]
    return cities, local_duration, swarm_duration, local_distance, swarm_distance


def plot_durations(cities, local_duration, swarm_duration, out_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(cities, local_duration, marker="o", label="Local")
    plt.plot(cities, swarm_duration, marker="o", label="Swarm")
    plt.xlabel("Número de ciudades")
    plt.ylabel("Duración promedio (s)")
    plt.title("Comparación de duración promedio: Local vs Swarm")
    plt.grid(True, alpha=0.3)
    plt.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def plot_best_distance(cities, local_dist, swarm_dist, out_path: Path) -> None:
    plt.figure(figsize=(8, 5))
    plt.plot(cities, local_dist, marker="o", label="Local")
    plt.plot(cities, swarm_dist, marker="o", label="Swarm")
    plt.xlabel("Número de ciudades")
    plt.ylabel("Mejor distancia promedio")
    plt.title("Mejor distancia promedio: Local vs Swarm")
    plt.grid(True, alpha=0.3)
    plt.legend()
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200)
    plt.close()


def save_duration_table_image(cities, local_duration, swarm_duration, out_path: Path) -> None:
    """Render the duration table to an image for quick sharing."""
    fig, ax = plt.subplots(figsize=(6, 0.6 * len(cities) + 1))
    ax.axis("off")

    table_data = [
        [n, f"{l:.4f}", f"{s:.4f}"] for n, l, s in zip(cities, local_duration, swarm_duration)
    ]
    table = ax.table(
        cellText=table_data,
        colLabels=["Ciudades", "Local (s)", "Swarm (s)"],
        cellLoc="center",
        colColours=["#ececec", "#ececec", "#ececec"],
        loc="center",
    )
    table.scale(1, 1.2)
    ax.set_title("Duración promedio por número de ciudades", pad=12)
    out_path.parent.mkdir(parents=True, exist_ok=True)
    plt.tight_layout()
    plt.savefig(out_path, dpi=200, bbox_inches="tight")
    plt.close(fig)


def main() -> None:
    base = Path(__file__).parent
    local_rows = load_metrics(base / "metrics-local.csv")
    swarm_rows = load_metrics(base / "metrics-swarm.csv")

    local_avg = avg_by_city(local_rows)
    swarm_avg = avg_by_city(swarm_rows)
    (
        cities,
        local_duration,
        swarm_duration,
        local_distance,
        swarm_distance,
    ) = build_series(local_avg, swarm_avg)

    plot_durations(cities, local_duration, swarm_duration, base / "duration_comparison.png")
    plot_best_distance(cities, local_distance, swarm_distance, base / "best_distance_comparison.png")
    save_duration_table_image(
        cities, local_duration, swarm_duration, base / "duration_table.png"
    )

    print("Duración promedio por número de ciudades:")
    print(f"{'Ciudades':>10} | {'Local (s)':>10} | {'Swarm (s)':>10}")
    print("-" * 36)
    for n, l, s in zip(cities, local_duration, swarm_duration):
        print(f"{n:10d} | {l:10.4f} | {s:10.4f}")

if __name__ == "__main__":
    main()
