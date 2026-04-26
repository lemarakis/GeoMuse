import os
import pandas as pd
import psycopg2
import datashader as ds
import datashader.transfer_functions as tf
import matplotlib.pyplot as plt
import contextily as cx
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

    df = pd.DataFrame(rows, columns=["x", "y"])
    return df


def generate_heatmap_with_basemap(df, output_path):
    # Ensure directory exists
    output_dir = os.path.dirname(output_path)
    if output_dir:
        os.makedirs(output_dir, exist_ok=True)

    zoom = 12
    width = 6000
    height = 4000
    alpha = 255
    cmap = ["black", "purple", "magenta", "red", "orange", "yellow", "white"]
    how = "eq_hist"

    # Manual Porto bounding box in EPSG:3857
    x_min = -972500
    x_max = -945000
    y_min = 5022000
    y_max = 5052500

    df = df[
        (df["x"] > x_min) & (df["x"] < x_max) &
        (df["y"] > y_min) & (df["y"] < y_max)
    ].copy()

    # Datashader
    canvas = ds.Canvas(
        plot_width=width,
        plot_height=height,
        x_range=(x_min, x_max),
        y_range=(y_min, y_max)
    )

    agg = canvas.points(df, "x", "y", agg=ds.count())

    img = tf.shade(agg, cmap=cmap, how=how)
    img = tf.dynspread(img, threshold=0.4, max_px=6)
    pil_img = img.to_pil().convert("RGBA")

    data = pil_img.load()
    w, h = pil_img.size

    for y in range(h):
        for x in range(w):
            r, g, b, a = data[x, y]

            if r < 5 and g < 5 and b < 5:
                data[x, y] = (0, 0, 0, 0)
            else:
                data[x, y] = (r, g, b, alpha)

    # Plot
    fig_w = 16
    fig_h = fig_w * (height / width)

    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)

    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)

    # Basemap κάτω
    cx.add_basemap(
        ax,
        crs="EPSG:3857",
        source=cx.providers.CartoDB.DarkMatterNoLabels,
        zoom=zoom
    )

    # Heatmap πάνω
    ax.imshow(
        pil_img,
        extent=(x_min, x_max, y_min, y_max),
        origin="upper"
    )

    ax.set_axis_off()
    plt.tight_layout(pad=0)
    plt.savefig(f"{output_path}.png", bbox_inches="tight", pad_inches=0)
    plt.close()


def main(output_path):
    df = load_points()
    generate_heatmap_with_basemap(df, output_path)


if __name__ == "__main__":
    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_map")
    main(output_file)