import os
import argparse
import subprocess
from common.utils import load_audio_files, is_package_installed, timer

def create_gmf_signatures(paths, output_path, args, verbose=False):
    # 2. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)

    # 3. Check if libsndfile1-dev is installed
    if not is_package_installed("libsndfile1-dev"):
        print("libsndfile1-dev is not installed")
        return
    
    # 4. Check if fftw3 is installed
    if not is_package_installed("fftw3"):
        print("fftw3 is not installed")
        return
    
    # 5. Check if fftw3-dev is installed
    if not is_package_installed("fftw3-dev"):
        print("fftw3-dev is not installed")
        return
    
    # 6. Check if pkg-config is installed
    if not is_package_installed("pkg-config"):
        print("pkg-config is not installed")
        return
    
    # 7. Check if the file GetMaxFreqs.cpp exists in the GetMaxFreqs directory
    if not os.path.exists("GetMaxFreqs/src/GetMaxFreqs.cpp"):
        print("GetMaxFreqs.cpp does not exist")
        return
    
    # 8. Compile GetMaxFreqs
    if subprocess.run(["g++", "-W", "-Wall", "-std=c++11", "-o", "GetMaxFreqs/bin/GetMaxFreqs", "GetMaxFreqs/src/GetMaxFreqs.cpp", "-lsndfile", "-lfftw3", "-lm"]).returncode != 0:
        print("Compilation failed")
        return
    
    # 9. Add permissions to GetMaxFreqs
    if subprocess.run(["chmod", "+x", "GetMaxFreqs/bin/GetMaxFreqs"]).returncode != 0:
        print("Failed to add permissions to GetMaxFreqs")
        return
    
    # 10. Generate signatures
    for path in paths:
        output_file = os.path.join(output_path, os.path.basename(path).rsplit('.', 1)[0] + ".freqs")
        if subprocess.run(["GetMaxFreqs/bin/GetMaxFreqs", "-w", output_file, args, path]).returncode != 0:
            print(f"Failed to generate signature for {path}")
            return
        
        if verbose:
            print(f"Generated signature for {path}")

@timer
def create_signatures(paths, output_path, signature_type, args, verbose=False):
    # 1. Select the signature type and create the signatures
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
