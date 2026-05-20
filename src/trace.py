"""
Trace GPS Processing Script

Processes GPS CSV files from Fitbit, generates static map images,
and outputs a summary CSV for PDF report generation.
"""

from pathlib import Path
from math import radians, cos, sin, asin, sqrt
import re

import geopandas as gpd
from shapely.geometry import Point
import reverse_geocoder as rg
import pandas as pd
import matplotlib.pyplot as plt
import contextily as ctx


BASE_DIR = Path(__file__).parent.parent
DATA_RAW_PATH = BASE_DIR / "data" / "data_raw_2025_10_10"
IMAGES_PATH = BASE_DIR / "data" / "images"

# Traces that are not real hikes (GPS triggered while stationary); skip them.
EXCLUDED_DATES = {
    "2015-12-23", "2015-12-24",
    "2016-01-12", "2016-01-13",
    "2016-03-28",
    "2016-04-05", "2016-04-06",
    "2016-05-13", "2016-05-14", "2016-05-28",
    "2016-06-24", "2016-06-25",
    "2016-07-28", "2016-07-29",
    "2016-08-31",
    "2016-09-01", "2016-09-03", "2016-09-07", "2016-09-08",
    "2016-11-10",
    "2017-02-25",
    "2017-04-15",
    "2017-06-30",
    "2017-07-24",
    "2017-08-05",
    "2017-12-28",
    "2018-05-03",
    "2018-09-07", "2018-09-08",
    "2019-08-23",
}


def haversine(lon1, lat1, lon2, lat2):
    lon1, lat1, lon2, lat2 = map(radians, [lon1, lat1, lon2, lat2])
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = sin(dlat/2)**2 + cos(lat1) * cos(lat2) * sin(dlon/2)**2
    return 2 * asin(sqrt(a)) * 6371


def process_trace(csv_path: Path, images_path: Path) -> dict:
    """Process one GPS trace CSV, save a map image, and return its metadata."""
    df = pd.read_csv(csv_path)

    date_str = re.search(r"\d{4}-\d{2}-\d{2}", csv_path.name).group(0)
    parts = date_str.split("-")
    date_rando = f"{parts[2]}/{parts[1]}/{parts[0]}"

    gdf = gpd.GeoDataFrame(
        df,
        geometry=[Point(xy) for xy in zip(df.longitude, df.latitude)],
        crs="EPSG:4326"
    )

    sample = gdf.iloc[::200].copy()
    coords = [(row.latitude, row.longitude) for _, row in sample.iterrows()]
    results = rg.search(coords)
    sample["locality"] = [r["name"] for r in results]
    sample = sample.drop_duplicates(subset=["locality"]).reset_index(drop=True)

    start_locality = sample.iloc[0]["locality"]

    gdf_3857 = gdf.to_crs(epsg=3857)
    sample_3857 = sample.to_crs(epsg=3857)

    distances = [
        haversine(df.loc[i, "longitude"], df.loc[i, "latitude"],
                  df.loc[i+1, "longitude"], df.loc[i+1, "latitude"])
        for i in range(len(df) - 1)
    ]
    distance_totale_km = sum(distances)

    timestamp = pd.to_datetime(df["timestamp"]).astype("int64") / 1e9
    duree_secondes = timestamp.iloc[-1] - timestamp.iloc[0]
    heures = int(duree_secondes // 3600)
    minutes = int((duree_secondes % 3600) // 60)
    secondes = int(duree_secondes % 60)

    fig, ax = plt.subplots(figsize=(12, 12))
    gdf_3857.plot(ax=ax, linewidth=2, color="blue", alpha=0.7)
    sample_3857.plot(ax=ax, color="red", markersize=50, alpha=0.8)

    for _, row in sample_3857.iterrows():
        ax.text(
            row.geometry.x, row.geometry.y, row.locality,
            fontsize=8, color="darkred", ha="left", va="bottom",
            bbox=dict(boxstyle="round,pad=0.3", facecolor="white", alpha=0.7, edgecolor="none")
        )

    ctx.add_basemap(ax, source=ctx.providers.OpenStreetMap.Mapnik, zorder=0)
    ax.set_axis_off()
    plt.tight_layout()
    plt.title(f"{start_locality} : {date_rando}", fontsize=16, pad=20)

    legend_text = (
        f"Durée totale : {heures:02d}h {minutes:02d}m {secondes:02d}s\n"
        f"Distance totale : {distance_totale_km:.3f} km"
    )
    ax.text(0.02, 0.98, legend_text, transform=ax.transAxes,
            fontsize=11, verticalalignment="top",
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.8))

    image_filename = f"trace_gps_{date_str}.png"
    plt.savefig(images_path / image_filename, dpi=150, bbox_inches="tight")
    plt.close(fig)

    return {
        "filename": image_filename,
        "localite_depart": start_locality,
        "date": date_rando,
    }


def main():
    images_metadata = []

    for csv_path in sorted(DATA_RAW_PATH.glob("*.csv")):
        date_str = re.search(r"\d{4}-\d{2}-\d{2}", csv_path.name).group(0)
        if date_str in EXCLUDED_DATES:
            print(f"Skipping {csv_path.name} (excluded)")
            continue
        print(f"Processing: {csv_path.name}")
        images_metadata.append(process_trace(csv_path, IMAGES_PATH))

    images_metadata.sort(key=lambda x: pd.to_datetime(x["date"], format="%d/%m/%Y"))
    pd.DataFrame(images_metadata).to_csv(IMAGES_PATH / "images_recap.csv", index=False)

    print(f"\nDone: {len(images_metadata)} images generated")
    print(f"Summary CSV: {IMAGES_PATH / 'images_recap.csv'}")


if __name__ == "__main__":
    main()
