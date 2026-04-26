import numpy as np
import matplotlib.pyplot as plt
import contextily as cx
import os
import config

def main():
    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_fake")
    
    # Δημιουργία 500.000 τυχαίων σημείων στα Βορειοανατολικά του Πόρτο
    center_x = -948000
    center_y = 5048000
    
    print("Generating fake points...")
    xs = np.random.normal(center_x, 1000, 500000)
    ys = np.random.normal(center_y, 1000, 500000)
    
    # Porto Bounding Box
    x_min, x_max = -972500, -945000
    y_min, y_max = 5022000, 5052500
    
    print("Creating the map...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    # Προσθήκη του φόντου (Basemap - Dark Matter)
    cx.add_basemap(ax, crs="EPSG:3857", source=cx.providers.CartoDB.DarkMatterNoLabels)
    
    # Σχεδιασμός του fake Heatmap
    ax.hexbin(xs, ys, gridsize=300, cmap="cool", alpha=0.8, mincnt=1)
    
    ax.set_axis_off()
    plt.tight_layout(pad=0)
    plt.savefig(f"{output_file}.png", bbox_inches="tight", pad_inches=0)
    plt.close()
    
    print(f"Porto Fake heatmap saved at: {output_file}.png")

if __name__ == "__main__":
    main()
