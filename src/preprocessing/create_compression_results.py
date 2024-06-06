import os
import argparse
import csv
from common.utils import load_audio_files, compress_file, compressors, timer

@timer
def create_compression_results(signature_paths, algorithm, output_path, verbose=False):
    # 1. Create the output directory if it does not exist
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    with open(output_path, "w") as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(["filename", "compressed_size"])

        for signature_path in signature_paths:
            with open(signature_path, "rb") as signature_file:
                # 2. Read the signature data
                audio_data = signature_file.read()

                # 3. Compress the signature data
                compressed_audio_data = compress_file(algorithm, audio_data)
                    
                # 4. Get the size of the compressed data
                compressed_size = len(compressed_audio_data)

                # 5. Write the results to the output file
                csv_writer.writerow([os.path.basename(signature_path), compressed_size])

                if verbose:
                    print(f"Compressed {signature_path} with {algorithm} to {compressed_size} bytes")
                            
def main():
    parser = argparse.ArgumentParser(description="Compress audio files and store the results in a file.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing audio files")
    parser.add_argument("-n", "--algorithm", type=str, help="Algorithms to compress files", default=list(compressors.keys())[0], choices=list(compressors.keys()))
    parser.add_argument("-o", "--output-path", type=str, help="Path to store the compression results", default="data/compression_results/{algorithm}/results.csv")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output", default=False)
    args = parser.parse_args()

    args.output_path = args.output_path.format(algorithm=args.algorithm)

    signature_paths = load_audio_files(args.paths, extensions=(".freqs"))
    
    create_compression_results(signature_paths, args.algorithm, args.output_path, args.verbose)

if __name__ == "__main__":
    main()
    
    