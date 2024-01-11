import os
import subprocess
import argparse
from tqdm import tqdm

def get_yaml_files(root_dir):
    folders = [folder for folder in os.listdir(root_dir) if os.path.isdir(os.path.join(root_dir, folder))]

    yaml_paths = []
    for folder in folders:
        yaml_path = os.path.join(root_dir, folder, f"{folder}.yaml")
        yaml_paths.append(yaml_path)
    return yaml_paths

def add_datasets(yaml_paths):
    total_yaml_paths = len(yaml_paths)

    for idx, yaml_path in enumerate(tqdm(yaml_paths, desc="Adding datasets", unit="dataset"), start=1):
        # Run the 'datacube dataset add' command using subprocess
        command = ['datacube', 'dataset', 'add', yaml_path]
        
        try:
            subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            print(f"Dataset added successfully from {yaml_path}")
        except subprocess.CalledProcessError as e:
            print(f"Error adding dataset from {yaml_path}: {e}")

        # Update the progress bar
        tqdm.write(f"Processed {idx}/{total_yaml_paths} YAML files")

if __name__ == "__main__":
    # Use argparse to get the root path from the command line
    parser = argparse.ArgumentParser(description="Add datasets to Data Cube from YAML files.")
    parser.add_argument("root_path", help="Root path containing folders with YAML files.")
    args = parser.parse_args()

    # Provide a list of YAML paths based on the root path
    yaml_paths = get_yaml_files(args.root_path)

    # Add datasets with progress bar
    add_datasets(yaml_paths)
