import os
import config
from heatmap.heatmap_generator_porto import main

if __name__ == "__main__":

    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto")
    main(output_file, how="eq_hist")
    print(f"Heatmap generated successfully: {output_file}.png")

    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_log")
    main(output_file, how="log")
    print(f"Heatmap generated successfully: {output_file}.png")

    output_file = os.path.join(config.HEATMAP_OUTPUT, "endpoints_heatmap_porto_linear")
    main(output_file, how="linear")
    print(f"Heatmap generated successfully: {output_file}.png")
