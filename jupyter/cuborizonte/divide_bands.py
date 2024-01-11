import argparse
import os
from tqdm import tqdm
import rasterio

def get_image_list(image_dir):
    image_list = []
    for root, dirs, files in os.walk(image_dir):
        for file in files:
            if file.endswith('.tif'):
                filename, _ = os.path.splitext(file)
                image_list.append(os.path.join(root, file))
    return image_list

def divide_rgb_bands(image_list, output_dir):
    total_images = len(image_list)

    for idx, image_path in enumerate(image_list, start=1):
        # Extract the file name without extension
        image_name = os.path.splitext(os.path.basename(image_path))[0]

        # Create output directory for the current image
        output_image_dir = os.path.join(output_dir, image_name)
        os.makedirs(output_image_dir, exist_ok=True)

        # Open the multi-band TIFF file
        with rasterio.open(image_path) as src:
            # Loop through each band
            with tqdm(total=src.count, desc=f'Processing {image_name}', unit='band') as pbar:
                for band_number in range(1, src.count + 1):
                    # Read the band data
                    band = src.read(band_number)

                    # Create a new TIFF file for each band
                    output_tif_path = os.path.join(output_image_dir, f'band_{band_number}.tif')
                    with rasterio.open(output_tif_path, 'w', driver='GTiff',
                                    width=src.width, height=src.height,
                                    count=1, dtype=band.dtype, crs=src.crs,
                                    transform=src.transform) as dst:
                        dst.write(band, 1)

                    # Update the progress bar
                    pbar.update(1)

        # ... (mesmo código)

def main():
    parser = argparse.ArgumentParser(description="Divide imagens RGB em bandas individuais.")
    parser.add_argument("input_dir", help="Caminho para o diretório de entrada contendo imagens TIFF.")
    parser.add_argument("output_dir", help="Caminho para o diretório de saída para as bandas processadas.")
    args = parser.parse_args()

    image_list = get_image_list(args.input_dir)
    divide_rgb_bands(image_list, args.output_dir)

if __name__ == '__main__':
    main()
