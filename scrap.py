import shutil
import subprocess
from datetime import datetime, timedelta

import pandas as pd
import os
from pathlib import Path

import glob
import pyarrow

def get_download_path():
    # Get the home directory
    home = Path.home()

    # Construct the download path
    download_path = os.path.join(home, "Downloads")

    return download_path


# Path to your .side file
def run_side(side_file_path, download_path, workdir):
    # Command to execute the .side file
    command = f'selenium-side-runner {side_file_path}'

    # Execute the command
    process = subprocess.Popen(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    # Wait for the command to complete
    stdout, stderr = process.communicate()

    if process.returncode == 0:
        print('Execution successful')
        print(stdout.decode())
    else:
        print('Execution failed')
        print(stderr.decode())


def move_files(source_dir, destination_dir):
    # Define the source and destination directories

    # Ensure the destination directory exists
    os.makedirs(destination_dir, exist_ok=True)

    # List all files in the source directory
    files = glob.glob(source_dir)
    dst_file_path = ''
    # Move each file from the source to the destination directory
    for file in files:
        src_file_path = os.path.join(source_dir, file)
        dst_file_path = os.path.join(destination_dir, os.path.basename(file))
        try:
            shutil.copyfile(src_file_path, dst_file_path)
            print(f'Copied: {file}')
        except Exception as e:
            print(f'Error moving {file}: {e}')
    return dst_file_path


def convert_to_parquet(param, workdir):
    # Read the CSV file
    df = pd.read_csv(param, delimiter=';', encoding='utf8', decimal=',')

    # Convert the CSV file to Parquet
    df.to_parquet(workdir + '\\' + 'IBOVDia.parquet', engine='pyarrow')

    print('Conversion to Parquet successful')


if __name__ == '__main__':

    side_file_path = 'tech-cha2.side'
    download_path = get_download_path()

    # Step 1: Run the Selenium IDE script
    run_side(side_file_path, download_path, os.getcwd())

    # Step 2: Move the downloaded file to the working directory
    dest_file = move_files(
        download_path + '\\' + 'IBOVDia_' + (datetime.now() - timedelta(days=1)).strftime('%d-%m-%y') + '.csv',
        os.getcwd() + '\\' + 'workdir\\')

    # Step 3: Convert the file to UTF-8 encoding
    with open(dest_file, 'r', encoding='windows-1252') as f:
        text = f.read()

    with open(dest_file, 'w', encoding='utf-8') as f:
        f.write(text)

    # Step 4: Remove the last character if it is a semicolon
    with open(dest_file, 'r', encoding='utf-8') as file, open(dest_file + '_temp.csv', 'w',
                                                              encoding='utf-8') as temp_file:
        for line in file:
            # Remove the last character if it is a semicolon
            if line.startswith('IBOV') or line.startswith('Quantidade') or line.startswith('Redutor'):
                continue
            if line.endswith(';\n'):
                line = line[:-2] + '\n'
            temp_file.write(line)

    # Replace the original file with the modified file
    os.replace(dest_file + '_temp.csv', dest_file)

    # Step 5: Convert the file to Parquet
    convert_to_parquet(dest_file, os.getcwd() + '\\' + 'workdir\\')

    print('Done!')
