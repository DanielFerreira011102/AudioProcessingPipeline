import os
import argparse
import random
import subprocess
from common.utils import load_audio_files, is_package_installed, timer

@timer
def create_audio_segment(audio_paths, output_path, duration, start_time=None, min_time=0, verbose=False):
    # 1. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)

    # 2. Check if SoX is installed
    if not is_package_installed("sox"):
        print("SoX is not installed")
        return

    for audio_path in audio_paths:
        # 3. Get the audio format of the audio file
        audio_format = audio_path.rsplit('.', 1)[1]

        # 4. Find the duration of the audio file
        audio_duration = float(subprocess.check_output(
            ["soxi", "-D", audio_path]
        ).strip())
        
        # 5. Check if the duration of the audio file is less than the duration of the segment
        if audio_duration < duration:
            print(f"Audio duration is less than {duration} seconds: {audio_path}")
            continue

        # 6. Check if the minimum time is less than the duration of the segment   
        if min_time >= audio_duration - duration:
            print(f"min_time is too large for audio file: {audio_path}")
            continue
        
        # 7. Check if the start time is less than the minimum time
        if start_time is not None and start_time < min_time:
            print(f"start_time is too small for audio file: {audio_path}")
            continue
        
        # 8. Check if the start time is less than the duration of the segment
        if start_time is not None and start_time > audio_duration - duration:
            print(f"start_time is too large for audio file: {audio_path}")
            continue
        
        # 9. Select the start time of the segment
        current_start_time = start_time if start_time is not None else random.uniform(min_time, audio_duration - duration)
        
        # 10. Create the output file
        output_file = os.path.join(output_path, f"{os.path.basename(audio_path).rsplit('.', 1)[0]}_{current_start_time}_{duration}.{audio_format}")

        # 11. Create the audio segment
        subprocess.run(
            ["sox", audio_path, output_file, "trim", str(current_start_time), str(duration)],
            check=True
        )

        if verbose:
            print(f"Created: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Create a segment of an audio file or files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration of the segment in seconds (default: 30)")
    parser.add_argument("-m", "--min-time", type=int, default=0, help="Minimum start time of the segment in seconds (default: 0)")
    parser.add_argument("-s", "--start-time", type=int, default=None, help="Start time of the segment in seconds (default: None). If None, the start time is randomly selected.")
    parser.add_argument("-o", "--output-path", default="data/segments/", help="Output path for audio segments (default: data/segments/)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output", default=False)
    args = parser.parse_args()

    audio_paths = load_audio_files(args.paths)
    
    create_audio_segment(audio_paths, args.output_path, args.duration, args.start_time, args.min_time, args.verbose)

if __name__ == "__main__":
    main()