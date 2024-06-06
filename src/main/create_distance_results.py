import os
import argparse
import csv
from itertools import product
from multiprocessing import Pool, Manager, cpu_count
from common.utils import load_audio_files, compress_file, compress_files, compressors, timer

def NCD(C_x, C_y, C_xy):
    num = C_xy - min(C_x, C_y)
    den = max(C_x, C_y)
    return num / den if den > 0 else 0

def read_file(filepath):
    with open(filepath, "rb") as file:
        return file.read()
    
def read_compression_results(filepath):
    if filepath is None or not os.path.exists(filepath) or not os.path.isfile(filepath):
        return {}
    
    with open(filepath, "r") as file:
        reader = csv.reader(file)
        next(reader)
        return {row[0]: int(row[1]) for row in reader}

def get_compressed_length(algorithm, data, cache, cache_key):
    if cache_key not in cache:
        cache[cache_key] = len(compress_file(algorithm, data))
    return cache[cache_key]

def compress_and_calculate(segment_signature_path, signature, algorithm, segment_signatures_cache, signatures_cache):
    segment_signature_name = os.path.basename(segment_signature_path)
    signature_name = os.path.basename(signature)
    
    x = read_file(segment_signature_path)
    y = read_file(signature)

    C_x = get_compressed_length(algorithm, x, segment_signatures_cache, segment_signature_name)
    C_y = get_compressed_length(algorithm, y, signatures_cache, signature_name)

    C_xy = len(compress_files(algorithm, x, y))

    ncd = NCD(C_x, C_y, C_xy)

    return segment_signature_name, signature_name, ncd

@timer
def create_results(segment_signature_paths, signature_paths, algorithm, output_path, x_compression_results_path, y_compression_results_path):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    
    with Manager() as manager:
        segment_cache = manager.dict(read_compression_results(x_compression_results_path))
        signature_cache = manager.dict(read_compression_results(y_compression_results_path))
        tasks = [
            (segment_path, signature_path, algorithm, segment_cache, signature_cache)
            for segment_path, signature_path in product(segment_signature_paths, signature_paths)
        ]
        
        with Pool(cpu_count()) as pool:
            results = pool.starmap(compress_and_calculate, tasks)
    
        with open(output_path, "w", newline='') as result_file:
            csv_writer = csv.writer(result_file)
            csv_writer.writerow(["segment_signature", "signature", "ncd"])
            csv_writer.writerows(results)

def main():
    parser = argparse.ArgumentParser(description="Find the most similar audio file in a database.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing the segment signatures")
    parser.add_argument("-x", "--x-compression-results-path", type=str, help="Path to store the compression results for the segment signatures", default=None)
    parser.add_argument("-y", "--y-compression-results-path", type=str, help="Path to store the compression results for the signatures", default=None)
    parser.add_argument("-d", "--database-path", type=str, help="Path to the database signatures", default="data/signatures/")
    parser.add_argument("-n", "--algorithm", type=str, help="Algorithm to compress files", default=list(compressors.keys())[0], choices=list(compressors.keys()))
    parser.add_argument("-o", "--output-path", type=str, help="Path to store the results", default="data/distances/{algorithm}/results.csv")
    args = parser.parse_args()

    args.output_path = args.output_path.format(algorithm=args.algorithm)

    segment_signature_paths = load_audio_files(args.paths, extensions=(".freqs"))
    signature_paths = load_audio_files([args.database_path], extensions=(".freqs"))
    
    create_results(
        segment_signature_paths, 
        signature_paths, 
        args.algorithm, 
        args.output_path, 
        args.x_compression_results_path, 
        args.y_compression_results_path,
    )

if __name__ == '__main__':
    main()
