import os
import subprocess
import csv
import gzip
import bz2
import lzma
import zstandard as zstd
import zlib
import lz4.frame as lz4
import snappy

# Compression utilities

compressors = {
    "gzip": gzip.compress,
    "bz2": bz2.compress,
    "lzma": lzma.compress,
    "zstd": zstd.ZstdCompressor().compress,
    "zlib": zlib.compress,
    "lz4": lz4.compress,
    "snappy": snappy.compress,
}

def compress_file(algorithm, data):
    compressor = compressors.get(algorithm)

    if not compressor:
        raise ValueError(f"Invalid compression algorithm: {algorithm}")
    
    return compressor(data)

def compress_files(algorithm, x, y):
    return compress_file(algorithm, x + y)

# File utilities

def load_audio_files(paths, extensions=(".mp3", ".wav")):
    audio_paths = set()
    
    for path in paths:
        if not os.path.exists(path):
            raise FileNotFoundError(f"Path not found: {path}")
        
        if os.path.isdir(path):
            audio_paths.update(os.path.join(path, file) for file in os.listdir(path) if file.endswith(extensions))

        if os.path.isfile(path) and path.endswith(extensions):
            audio_paths.add(path)

    if not audio_paths:
        raise FileNotFoundError("No audio files found")
    
    return audio_paths

def load_audio_urls(urls, file_paths):
    urls = set(urls)

    for file_path in file_paths:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Path not found: {file_path}")

        if os.path.isdir(file_path):
            for file in os.listdir(file_path):
                with open(os.path.join(file_path, file), 'r') as file:
                    urls.update(line.strip() for line in file if line.strip())

        if os.path.isfile(file_path):
            with open(file_path, 'r') as file:
                urls.update(line.strip() for line in file if line.strip())

    if not urls:
        raise FileNotFoundError("No URLs found")
    
    return urls

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

# Package utilities

def is_package_installed(package_name):
    result = subprocess.run(["dpkg", "-l", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

# Timing utilities

def timer(func):
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        end = time.time()
        print(f"{func.__name__} executed in {end - start} seconds")
        return result
    return wrapper