import os
import argparse
import subprocess

def is_package_installed(package_name):
    result = subprocess.run(["dpkg", "-l", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def create_gmf_signatures(paths, output_path, args):    
    # 1. Check if libsndfile1-dev is installed
    if not is_package_installed("libsndfile1-dev"):
        print("libsndfile1-dev is not installed")
        return
    
    # 2. Check if fftw3 is installed
    if not is_package_installed("fftw3"):
        print("fftw3 is not installed")
        return
    
    # 3. Check if fftw3-dev is installed
    if not is_package_installed("fftw3-dev"):
        print("fftw3-dev is not installed")
        return
    
    # 4. Check if pkg-config is installed
    if not is_package_installed("pkg-config"):
        print("pkg-config is not installed")
        return
    
   # 5. Check if the file GetMaxFreqs.cpp exists in the GetMaxFreqs directory
    if not os.path.exists("GetMaxFreqs/src/GetMaxFreqs.cpp"):
        print("GetMaxFreqs.cpp does not exist")
        return
    
    # 6. Compile GetMaxFreqs
    if subprocess.run(["g++", "-W", "-Wall", "-std=c++11", "-o", "GetMaxFreqs/bin/GetMaxFreqs", "GetMaxFreqs/src/GetMaxFreqs.cpp", "-lsndfile", "-lfftw3", "-lm"]).returncode != 0:
        print("Compilation failed")
        return
    
    # 7. Add permissions to GetMaxFreqs
    if subprocess.run(["chmod", "+x", "GetMaxFreqs/bin/GetMaxFreqs"]).returncode != 0:
        print("Failed to add permissions to GetMaxFreqs")
        return
    
    # 8. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)
    
    # 9. Generate signatures
    for path in paths:
        output_file = os.path.join(output_path, os.path.splitext(os.path.basename(path))[0] + ".gmf")
        if subprocess.run(["GetMaxFreqs/bin/GetMaxFreqs", "-w", output_file, args, path]).returncode != 0:
            print(f"Failed to generate signature for {path}")
            return
        print(f"Generated signature for {path}")

def create_signatures(paths, output_path, signature_type, args):
    match signature_type:
        case "gmf":
            create_gmf_signatures(paths, output_path, args)
        case _:
            print(f"Invalid signature type: {signature_type}")
            return

def main():
    parser = argparse.ArgumentParser(description="Generate audio signatures from audio files.")
    parser.add_argument("paths", nargs="+", type=str, help="Path to audio files or directories containing audio files")
    parser.add_argument("-o", "--output-path", type=str, default="data/signatures/", help="Output path for signatures (default: data/signatures/)")
    parser.add_argument("-n", "--signature-type", type=str, default="gmf", help="Type of signature to generate (default: gmf)")
    parser.add_argument("-x", "--args", type=str, default="", help="Arguments for the signature type")
    args = parser.parse_args()
    
    audio_paths = set()

    for path in args.paths:
        if not os.path.exists(path):
            print(f"Path does not exist: {path}")
            return
        
        if os.path.isdir(path):
            audio_paths.update(os.path.join(path, file) for file in os.listdir(path) if file.endswith((".mp3", ".wav")))

        if os.path.isfile(path) and path.endswith((".mp3", ".wav")):
            audio_paths.add(path)

    if not audio_paths:
        print("No audio files found")
        return
    
    create_signatures(audio_paths, args.output_path, args.signature_type, args.args)

if __name__ == "__main__":
    main()
