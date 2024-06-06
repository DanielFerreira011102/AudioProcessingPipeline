import os
import argparse
import random
from pydub import AudioSegment

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

def create_audio_segment(audio_paths, output_path, duration, start_time=None, min_time=0):
    # 1. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)

    for audio_path in audio_paths:
        audio_format = audio_path.rsplit('.', 1)[1]

        # 2. Load the audio file
        audio = AudioSegment.from_file(audio_path)
        
        if audio.duration_seconds < duration:
            print(f"Audio duration is less than {duration} seconds: {audio_path}")
            continue
        
        if min_time >= audio.duration_seconds - duration:
            print(f"min_time is too large for audio file: {audio_path}")
            continue
        
        # 3. Select the start time of the segment
        if start_time is None:
            current_start_time = random.randint(min_time, int(audio.duration_seconds - duration))
        else:
            if start_time < min_time or start_time > audio.duration_seconds - duration:
                print(f"Invalid start_time for audio file: {audio_path}")
                continue
            current_start_time = start_time

        # 4. Create the audio segment
        audio_segment = audio[current_start_time * 1000:(current_start_time + duration) * 1000]
        
        output_file = os.path.join(output_path, f"{os.path.basename(audio_path).rsplit('.', 1)[0]}_{current_start_time}s_{duration}s.{audio_format}")

        # 5. Export the audio segment
        audio_segment.export(output_file, format=audio_format)

        print(f"Created: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Create a segment of an audio file or files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration of the segment in seconds (default: 30)")
    parser.add_argument("-m", "--min-time", type=int, default=0, help="Minimum start time of the segment in seconds (default: 0)")
    parser.add_argument("-s", "--start-time", type=int, default=None, help="Start time of the segment in seconds (default: None). If None, the start time is randomly selected.")
    parser.add_argument("-o", "--output-path", default="data/segments/", help="Output path for audio segments (default: data/segments/)")
    args = parser.parse_args()

    audio_paths = load_audio_files(args.paths)
    
    create_audio_segment(audio_paths, args.output_path, args.duration, args.start_time, args.min_time)

if __name__ == "__main__":
    main()