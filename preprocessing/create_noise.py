import os
import argparse
import subprocess
import tempfile
from pydub import AudioSegment
import numpy as np

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

def is_package_installed(package_name):
    result = subprocess.run(["dpkg", "-l", package_name], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    return result.returncode == 0

def add_sox_noise(audio_paths, noise_type, intensity, output_path):
    # 3. Check if SoX is installed
    if not is_package_installed("sox"):
        print("SoX is not installed")
        return

    for audio_path in audio_paths:
        filename = os.path.basename(audio_path)
        output_file = os.path.join(output_path, filename)
        audio_format = audio_path.rsplit('.', 1)[1]

        # 4. Create temporary noise file
        temp_noise_file_path = tempfile.mktemp(suffix=f'.{audio_format}')

        # 5. Find the duration, sample rate, and number of channels of the audio file
        duration = subprocess.check_output(
            ["soxi", "-D", audio_path]
        ).strip()
        sample_rate = subprocess.check_output(
            ["soxi", "-r", audio_path]
        ).strip()
        channels = subprocess.check_output(
            ["soxi", "-c", audio_path]
        ).strip()

        # 6. Select the noise effect based on the noise type
        match noise_type:
            case "white":
                noise_effect = "whitenoise"
            case "pink":
                noise_effect = "pinknoise"
            case "brown", "red":
                noise_effect = "brownnoise"
            case _:
                print(f"Unknown noise type: {noise_type}")
                return

        # 7. Add noise to the audio file
        subprocess.run(
            ["sox", "-n", "-r", sample_rate, "-c", channels, temp_noise_file_path, "synth", duration.decode('utf-8'), noise_effect, "vol", str(intensity)],
            check=True
        )

        # 8. Mix the audio file with the noise
        subprocess.run(
            ["sox", "-m", audio_path, temp_noise_file_path, output_file],
            check=True
        )

        # 9. Remove the temporary noise file
        os.remove(temp_noise_file_path)

def add_video_noise(audio_paths, intensity, ids, output_path):
    # 3. Check if yt-dlp is installed
    if not is_package_installed("yt-dlp"):
        print("yt-dlp is not installed")
        return
    
    sample_audio_path = next(iter(audio_paths))

    sample_audio = AudioSegment.from_file(sample_audio_path)

    audio_format = sample_audio_path.rsplit('.', 1)[1]
    sample_rate = sample_audio.frame_rate
    channels = sample_audio.channels
    bits_per_sample = sample_audio.sample_width * 8
    
    # 4. Group audio paths by video ID
    audio_paths_by_id = [[] for _ in range(len(ids))]
    for audio_path in audio_paths:
        idx = np.random.randint(len(ids))
        audio_paths_by_id[idx].append(audio_path)

    for id_, audio_paths in zip(ids, audio_paths_by_id):
        # 5. Create temporary audio file
        temp_audio_path = tempfile.mktemp(suffix=f'.{audio_format}')

        # 6. Download audio from YouTube
        subprocess.run(
            [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--output', temp_audio_path,
                '--extract-audio',
                '--audio-format', audio_format,
                '--audio-quality', '192',
                '--postprocessor-args', f'ffmpeg_o:-ar {sample_rate} -ac {channels} -sample_fmt s{bits_per_sample}',
                id_
            ], 
            check=True
        )

        # 7. Get the duration of the overlay noise
        overlay_noise_duration = float(subprocess.check_output(
            ["soxi", "-D", temp_audio_path]
        ).strip())

        for audio_path in audio_paths:
            filename = os.path.basename(audio_path)
            output_file = os.path.join(output_path, filename)

            # 8. Get the duration of the audio file
            noise_duration = float(subprocess.check_output(
                ["soxi", "-D", audio_path]
            ).strip())

            noise_start = np.random.uniform(0, overlay_noise_duration - noise_duration)

            # 9. Create temporary trimmed audio file
            trimmed_audio_path = tempfile.mktemp(suffix=f'.{audio_format}')

            # 10. Trim the overlay noise
            subprocess.run(
                ["sox", temp_audio_path, trimmed_audio_path, "trim", str(noise_start), str(noise_duration)],
                check=True
            )

            # 11. Mix the audio file with the overlay noise
            subprocess.run(
                ["sox", "-m", "-v", "1", audio_path, "-v", str(intensity), trimmed_audio_path, output_file],
                check=True,
                stderr=subprocess.DEVNULL
            )

            print(f"Added noise to {audio_path}")

            # 12. Remove the temporary trimmed audio file
            os.remove(trimmed_audio_path)

        # 13. Remove the temporary audio file
        os.remove(temp_audio_path)


def add_noise(audio_paths, output_path, noise_type, intensity, ids):
    # 1. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)

    # 2. Select the noise type and add noise to the audio files
    match noise_type:
        case "video":
            add_video_noise(audio_paths, intensity, ids, output_path)
        case _:
            add_sox_noise(audio_paths, noise_type, intensity, output_path)

def main():
    parser = argparse.ArgumentParser(description="Add some noise to audio files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-o", "--output-path", default="data/noise/{noise_type}/{intensity}/", help="Output path for audio segments (default: data/noise/)")
    parser.add_argument("-n", "--noise-type", default="white", choices=["white", "pink", "brown", "red", "video"], help="Type of noise to add (default: white)")
    parser.add_argument("-y", "--ids", nargs="+", help="YouTube video IDs for custom noise")
    parser.add_argument("-i", "--intensity", type=float, default=1.0, help="Intensity of the noise (default: 1.0)")
    args = parser.parse_args()

    args.output_path = args.output_path.format(noise_type=args.noise_type, intensity=args.intensity)

    audio_paths = load_audio_files(args.paths)
        
    add_noise(audio_paths, args.output_path, args.noise_type, args.intensity, args.ids)

if __name__ == "__main__":
    main()
