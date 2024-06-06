import os
import argparse
import csv
import gzip
import bz2
import lzma

def load_signature_files(paths, extensions=(".freqs")):
    signature_paths = set()
    
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        
        if os.path.isdir(path):
            signature_paths.update(os.path.join(path, file) for file in os.listdir(path) if file.endswith(extensions))

        if os.path.isfile(path) and path.endswith(extensions):
            signature_paths.add(path)

    if not signature_paths:
        raise FileNotFoundError("No signature files found")

    return signature_paths

def gzip_compress(data):
    return gzip.compress(data)

def bz2_compress(data):
    return bz2.compress(data)

def lzma_compress(data):
    return lzma.compress(data)

def compress_file(algorithm, data):
    compressors = {
        "gzip": gzip_compress,
        "bz2": bz2_compress,
        "lzma": lzma_compress
    }
    compressor = compressors.get(algorithm)
    if compressor:
        return len(compressor(data))
    raise ValueError(f"Unknown algorithm: {algorithm}")

def create_compression_results(signature_paths, algorithm, output_path):
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
                            
def main():
    parser = argparse.ArgumentParser(description="Compress audio files and store the results in a file.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing audio files")
    parser.add_argument("-x", "--algorithm", type=str, help="Algorithms to compress files", default="gzip", choices=["gzip", "bz2", "lzma"])
    parser.add_argument("-o", "--output-path", type=str, help="Path to store the compression results", default="data/compression_results/{algorithm}/results.csv")
    args = parser.parse_args()

    args.output_path = args.output_path.format(algorithm=args.algorithm)

    signature_paths = load_signature_files(args.paths)
    
    create_compression_results(signature_paths, args.algorithm, args.output_path)

if __name__ == "__main__":
    main()
    
    