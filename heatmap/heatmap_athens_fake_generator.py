import numpy as np
import matplotlib.pyplot as plt
import contextily as cx
import os
import config

def main():
    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_athens_fake")
    
    # Δημιουργία 500.000 τυχαίων σημείων στα Βορειοανατολικά της Αττικής
    center_x = 2670000
    center_y = 4605000
    
    print("Generating fake points for Athens...")
    xs = np.random.normal(center_x, 1200, 500000)
    ys = np.random.normal(center_y, 1200, 500000)
    
    # Athens Bounding Box
    x_min, x_max = 2610000, 2690000
    y_min, y_max = 4540000, 4615000
    
    print("Creating the Athens map...")
    fig, ax = plt.subplots(figsize=(12, 8), dpi=200)
    ax.set_xlim(x_min, x_max)
    ax.set_ylim(y_min, y_max)
    
    # Προσθήκη του Basemap - Dark Matter χωρίς labels
    cx.add_basemap(ax, crs="EPSG:3857", source=cx.providers.CartoDB.DarkMatterNoLabels)
    
    # Σχεδιασμός του fake Heatmap
    ax.hexbin(xs, ys, gridsize=300, cmap="cool", alpha=0.8, mincnt=1)
    
    ax.set_axis_off()
    plt.tight_layout(pad=0)
    plt.savefig(f"{output_file}.png", bbox_inches="tight", pad_inches=0)
    plt.close()
    
    print(f"Athens fake heatmap saved at: {output_file}.png")

if __name__ == "__main__":
    main()
