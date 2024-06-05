import os
import argparse
import csv
import gzip
import bz2
import lzma
from itertools import product
from multiprocessing import Pool, Manager, cpu_count

def gzip_compress(data):
    return gzip.compress(data)

def bz2_compress(data):
    return bz2.compress(data)

def lzma_compress(data):
    return lzma.compress(data)

def load_signatures(signatures_path):
    return [os.path.join(signatures_path, file) for file in os.listdir(signatures_path) if os.path.isfile(os.path.join(signatures_path, file))]

def load_compression_results(compression_results_path):
    results = {}
    if compression_results_path:
        with open(compression_results_path, "r") as result_file:
            reader = csv.reader(result_file)
            next(reader)
            for row in reader:
                filename, compression_result = row
                results[filename] = int(compression_result)
    return results

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

def compress_files(algorithm, x, y):
    return compress_file(algorithm, x + y)

def NCD(C_x, C_y, C_xy):
    return (C_xy - min(C_x, C_y)) / max(C_x, C_y)

def compress_and_calculate(segment_signature_path, signature, algorithm, segment_signatures_cache, signatures_cache):
    segment_signature_name = os.path.basename(segment_signature_path)
    signature_name = os.path.basename(signature)
    
    if segment_signature_name not in segment_signatures_cache:
        with open(segment_signature_path, "rb") as segment_signature_file:
            x = segment_signature_file.read()
            C_x = compress_file(algorithm, x)
            segment_signatures_cache[segment_signature_name] = (x, C_x)
    else:
        x, C_x = segment_signatures_cache[segment_signature_name]

    if signature_name not in signatures_cache:
        with open(signature, "rb") as signature_file:
            y = signature_file.read()
            C_y = compress_file(algorithm, y)
            signatures_cache[signature_name] = (y, C_y)
    else:
        y, C_y = signatures_cache[signature_name]

    C_xy = compress_files(algorithm, x, y)
    ncd = NCD(C_x, C_y, C_xy)

    return segment_signature_name, signature_name, ncd

def create_results(segment_signatures_paths, signatures_path, algorithm, compression_results_path, output_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    signatures = load_signatures(signatures_path)

    manager = Manager()
    segment_signatures_cache = manager.dict()
    signatures_cache = manager.dict()
    signatures_cache.update(load_compression_results(compression_results_path))
    results = []

    with Pool(cpu_count()) as pool:
        tasks = [
            (segment_signature_path, signature, algorithm, segment_signatures_cache, signatures_cache)
            for segment_signature_path, signature in product(segment_signatures_paths, signatures)
        ]
        results = pool.starmap(compress_and_calculate, tasks)

    with open(output_path, "w", newline='') as result_file:
        csv_writer = csv.writer(result_file)
        csv_writer.writerow(["segment_signature", "signature", "ncd"])
        csv_writer.writerows(results)

def main():
    parser = argparse.ArgumentParser(description="Find the most similar audio file in a database.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing the segment signatures")
    parser.add_argument("-s", "--signatures-path", type=str, help="Path to signatures", default="data/signatures/")
    parser.add_argument("-x", "--algorithm", type=str, help="Algorithm to compress files", default="gzip", choices=["gzip", "bz2", "lzma"])
    parser.add_argument("-y", "--compression-results-path", type=str, help="Path to the pre-computed compression results of the database files", default=None)
    parser.add_argument("-o", "--output-path", type=str, help="Path to store the results", default="data/distance_results/{algorithm}/results.csv")
    args = parser.parse_args()

    args.output_path = args.output_path.format(algorithm=args.algorithm)

    segment_signatures_paths = set()
    for path in args.paths:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return
        if os.path.isdir(path):
            segment_signatures_paths.update(os.path.join(path, file) for file in os.listdir(path) if os.path.isfile(os.path.join(path, file)))
        elif os.path.isfile(path):
            segment_signatures_paths.add(path)

    if not segment_signatures_paths:
        print("No segment signatures found")
        return
    
    create_results(segment_signatures_paths, args.signatures_path, args.algorithm, args.compression_results_path, args.output_path)

if __name__ == '__main__':
    main()
