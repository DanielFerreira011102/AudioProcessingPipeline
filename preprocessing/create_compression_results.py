import os
import argparse
import csv

import gzip
import bz2
import lzma

def gzip_compress(data):
    return gzip.compress(data)

def bz2_compress(data):
    return bz2.compress(data)

def lzma_compress(data):
    return lzma.compress(data)

def create_compression_results(audio_paths, algorithm, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(["filename", "compressed_size"])

        for audio_path in audio_paths:
            with open(audio_path, "rb") as audio_file:
                audio_data = audio_file.read()

                match algorithm:
                    case "gzip":
                        compressed_audio_data = gzip_compress(audio_data)
                    case "bz2":
                        compressed_audio_data = bz2_compress(audio_data)
                    case "lzma":
                        compressed_audio_data = lzma_compress(audio_data)
                    case _:
                        print(f"Unknown algorithm: {algorithm}")
                        return
                    
                compressed_size = len(compressed_audio_data)
                csv_writer.writerow([os.path.basename(audio_path), compressed_size])
                            
def main():
    parser = argparse.ArgumentParser(description="Compress audio files and store the results in a file.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing audio files")
    parser.add_argument("-x", "--algorithm", type=str, help="Algorithms to compress files", default="gzip", choices=["gzip", "bz2", "lzma"])
    parser.add_argument("-o", "--output-path", type=str, help="Path to store the compression results", default="data/compression_results/{algorithm}/results.csv")
    args = parser.parse_args()

    args.output_path = args.output_path.format(algorithm=args.algorithm)

    audio_paths = set()

    for path in args.paths:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return
        
        if os.path.isdir(path):
            audio_paths.update({os.path.join(path, audio_file) for audio_file in os.listdir(path)})

        elif os.path.isfile(path):
            audio_paths.add(path)

    if not audio_paths:
        print("No audio files found")
        return
    
    create_compression_results(audio_paths, args.algorithm, args.output_path)

if __name__ == "__main__":
    main()
    
    