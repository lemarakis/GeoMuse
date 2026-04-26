import os
import pandas as pd
import psycopg2
import datashader as ds
import datashader.transfer_functions as tf
from dotenv import load_dotenv

import config

load_dotenv()

def get_conn():
    return psycopg2.connect(
        host=os.getenv("DB_HOST"),
        dbname=os.getenv("DB_NAME"),
        user=os.getenv("DB_USER"),
        password=os.getenv("DB_PASS"),
        port=os.getenv("DB_PORT", "5432")
    )

def load_points():
    geom_col = "end_point"
    query = f"""
        SELECT
            ST_X(ST_Transform({geom_col}, 3857)) AS x,
            ST_Y(ST_Transform({geom_col}, 3857)) AS y
        FROM taxi_trips
        WHERE {geom_col} IS NOT NULL
    """

    conn = get_conn()
    cur = conn.cursor()
    cur.execute(query)
    rows = cur.fetchall()
    cur.close()
    conn.close()
    return pd.DataFrame(rows, columns=["x", "y"])


def generate_heatmap(df, output_path, how="eq_hist"):
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    cmap = ["lightblue", "blue", "purple", "red", "yellow"]
    #cmap = ["black", "darkblue", "blue", "magenta", "red", "orange", "yellow", "white"]
    #cmap = ["black", "purple", "magenta", "red", "orange", "yellow", "white"]
    width = 6000
    height = 4000
    background = "black"

    #manual Porto bounding box
    x_min = -972500
    x_max = -945000
    y_min = 5022000
    y_max = 5052500

    df = df[
        (df["x"] > x_min) & (df["x"] < x_max) &
        (df["y"] > y_min) & (df["y"] < y_max)
    ]

    canvas = ds.Canvas(
        plot_width=width,
        plot_height=height,
        x_range=(x_min, x_max),
        y_range=(y_min, y_max)
    )

    agg = canvas.points(df, "x", "y", agg=ds.count())
    img = tf.shade(agg, cmap=cmap, how=how)
    img = tf.set_background(img, background)

    img.to_pil().save(f"{output_path}.png")


def main(output_path, how="eq_hist"):
    df = load_points()
    generate_heatmap(df, output_path, how=how)


if __name__ == "__main__":
    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto")
    main(output_file)
