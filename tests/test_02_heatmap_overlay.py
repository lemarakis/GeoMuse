import os
import config
from heatmap.heatmap_map_overlay import main

if __name__ == "__main__":

    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_overlay")
    main(output_file)
    print(f"Overlay Heatmap generated successfully: {output_file}.png")
