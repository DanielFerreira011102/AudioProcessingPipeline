import os
import argparse
import random
from pydub import AudioSegment

def create_audio_segment(audio_paths, output_path, duration, start_time=None):
    os.makedirs(output_path, exist_ok=True)

    for audio_path in audio_paths:
        audio_format = audio_path.rsplit('.', 1)[1]

        audio = AudioSegment.from_file(audio_path)
        
        if audio.duration_seconds < duration:
            print(f"Audio duration is less than {duration} seconds: {audio_path}")
            continue

        current_start_time = random.randint(0, int(audio.duration_seconds - duration)) if start_time is None else start_time

        audio_segment = audio[current_start_time * 1000:(current_start_time + duration) * 1000]

        output_file = os.path.join(output_path, f"{os.path.basename(audio_path).rsplit('.', 1)[0]}_{current_start_time}s_{duration}s.{audio_format}")

        audio_segment.export(output_file, format=audio_format)
        print(f"Created: {output_file}")
    

def main():
    parser = argparse.ArgumentParser(description="Create a segment of an audio file or files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-d", "--duration", type=int, default=5, help="Duration of the segment in seconds (default: 30)")
    parser.add_argument("-s", "--start-time", type=int, default=None, help="Start time of the segment in seconds (default: None). If None, the start time is randomly selected.")
    parser.add_argument("-o", "--output-path", default="data/segments/", help="Output path for audio segments (default: data/segments/)")
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
    
    create_audio_segment(audio_paths, args.output_path, args.duration, args.start_time)

if __name__ == "__main__":
    main()