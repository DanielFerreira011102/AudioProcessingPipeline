import os
import argparse
import subprocess
from multiprocessing import Pool, cpu_count
from common.utils import load_audio_files, is_package_installed, timer

def compile_get_max_freqs():
    if not os.path.exists("GetMaxFreqs/src/GetMaxFreqs.cpp"):
        print("GetMaxFreqs.cpp does not exist")
        return False

    if subprocess.run(["g++", "-W", "-Wall", "-std=c++11", "-o", "GetMaxFreqs/bin/GetMaxFreqs", "GetMaxFreqs/src/GetMaxFreqs.cpp", "-lsndfile", "-lfftw3", "-lm"]).returncode != 0:
        print("Compilation failed")
        return False

    if subprocess.run(["chmod", "+x", "GetMaxFreqs/bin/GetMaxFreqs"]).returncode != 0:
        print("Failed to add permissions to GetMaxFreqs")
        return False

    return True

def check_dependencies():
    dependencies = ["libsndfile1-dev", "fftw3", "fftw3-dev", "pkg-config"]
    for dep in dependencies:
        if not is_package_installed(dep):
            print(f"{dep} is not installed")
            return False
    return True

def generate_signature(args):
    path, output_path, signature_args = args
    output_file = os.path.join(output_path, os.path.basename(path).rsplit('.', 1)[0] + ".freqs")
    signature_args = signature_args.split()
    if subprocess.run(["GetMaxFreqs/bin/GetMaxFreqs", "-w", output_file] + signature_args + [path]).returncode != 0:
        print(f"Failed to generate signature for {path}")
        return False
    return True

def create_gmf_signatures(paths, output_path, args, verbose=False):
    os.makedirs(output_path, exist_ok=True)

    if not check_dependencies() or not compile_get_max_freqs():
        return

    with Pool(cpu_count()) as pool:
        tasks = [(path, output_path, args) for path in paths]
        results = pool.map(generate_signature, tasks)

    if verbose:
        for path, result in zip(paths, results):
            if result:
                print(f"Generated signature for {path}")
            else:
                print(f"Failed to generate signature for {path}")

@timer
def create_signatures(paths, output_path, signature_type, args, verbose=False):
    match signature_type:
        case "gmf":
            create_gmf_signatures(paths, output_path, args, verbose)
        case _:
            print(f"Invalid signature type: {signature_type}")
            return

def main():
    parser = argparse.ArgumentParser(description="Generate audio signatures from audio files.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing audio files")
    parser.add_argument("-o", "--output-path", type=str, default="data/signatures/{signature_type}", help="Output path for signatures (default: data/signatures/{signature_type})")
    parser.add_argument("-n", "--signature-type", type=str, default="gmf", help="Type of signature to generate", choices=["gmf"])
    parser.add_argument("-z", "--signature-args", nargs='?', type=str, const="", default="", help="Arguments for the signature type")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output", default=False)
    args = parser.parse_args()

    args.output_path = args.output_path.format(signature_type=args.signature_type)
    
    audio_paths = load_audio_files(args.paths)
    
    create_signatures(audio_paths, args.output_path, args.signature_type, args.signature_args, args.verbose)

if __name__ == "__main__":
    main()