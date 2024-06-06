import os
import argparse
import subprocess
import tempfile
import numpy as np
from common.utils import load_audio_files, is_package_installed, timer

def add_sox_noise(audio_paths, noise_type, intensity, output_path, verbose):
    # 3. Check if SoX is installed
    if not is_package_installed("sox"):
        print("SoX is not installed")
        return

    for audio_path in audio_paths:
        filename = os.path.basename(audio_path)
        output_file = os.path.join(output_path, filename)

        # 4. Get the audio format of the audio file
        audio_format = audio_path.rsplit('.', 1)[1]

        # 5. Create temporary noise file
        temp_noise_file_path = tempfile.mktemp(suffix=f'.{audio_format}')
        
        # 6. Find the duration of the audio file
        duration = float(subprocess.check_output(
            ["soxi", "-D", audio_path]
        ).strip())

        # 7. Find the sample rate of the audio file
        sample_rate = int(subprocess.check_output(
            ["soxi", "-r", audio_path]
        ).strip())

        # 8. Find the number of channels of the audio file
        channels = int(subprocess.check_output(
            ["soxi", "-c", audio_path]
        ).strip())

        # 9. Select the noise effect based on the noise type
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

        # 9. Add noise to the audio file
        subprocess.run(
            ["sox", "-n", "-r", str(sample_rate), "-c", str(channels), temp_noise_file_path, "synth", str(duration), noise_effect, "vol", str(intensity)],
            check=True
        )

        # 10. Mix the audio file with the noise
        subprocess.run(
            ["sox", "-m", audio_path, temp_noise_file_path, output_file],
            check=True
        )

        # 11. Remove the temporary noise file
        os.remove(temp_noise_file_path)

        if verbose:
            print(f"Added noise to {audio_path}")

def add_video_noise(audio_paths, intensity, ids, output_path, verbose):
    # 3. Check if yt-dlp is installed
    if not is_package_installed("yt-dlp"):
        print("yt-dlp is not installed")
        return
    
    # 4. Get a sample audio path
    sample_audio_path = next(iter(audio_paths))

    # 5. Get the audio format of the audio file
    audio_format = sample_audio_path.rsplit('.', 1)[1]

    # 6. Find the sample rate of the audio file
    sample_rate = int(subprocess.check_output(
        ["soxi", "-r", sample_audio_path]
    ).strip())

    # 7. Find the number of channels of the audio file
    channels = int(subprocess.check_output(
        ["soxi", "-c", sample_audio_path]
    ).strip())

    # 8. Find the number of bits per sample of the audio file
    bits_per_sample = int(subprocess.check_output(
        ["soxi", "-b", sample_audio_path]
    ).strip())
    
    # 9. Group audio paths by video ID
    audio_paths_by_id = [[] for _ in range(len(ids))]
    for audio_path in audio_paths:
        idx = np.random.randint(len(ids))
        audio_paths_by_id[idx].append(audio_path)

    for id_, audio_paths in zip(ids, audio_paths_by_id):
        # 10. Create temporary audio file
        temp_audio_path = tempfile.mktemp(suffix=f'.{audio_format}')

        # 11. Download audio from YouTube
        subprocess.run(
            [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--output', temp_audio_path,
                '--extract-audio',
                '--audio-format', audio_format,
                '--audio-quality', '192',
                '--postprocessor-args', f'ffmpeg_o:-ar {sample_rate} -ac {channels} -sample_fmt s{bits_per_sample}',
                '--quiet' if not verbose else '',
                f"https://www.youtube.com/watch?v={id_}"
            ], 
            check=True
        )

        # 12. Get the duration of the overlay noise
        overlay_noise_duration = float(subprocess.check_output(
            ["soxi", "-D", temp_audio_path]
        ).strip())

        for audio_path in audio_paths:
            filename = os.path.basename(audio_path)
            output_file = os.path.join(output_path, filename)

            # 13. Get the duration of the audio file
            noise_duration = float(subprocess.check_output(
                ["soxi", "-D", audio_path]
            ).strip())

            noise_start = np.random.uniform(0, overlay_noise_duration - noise_duration)

            # 14. Create temporary trimmed audio file
            trimmed_audio_path = tempfile.mktemp(suffix=f'.{audio_format}')

            # 15. Trim the overlay noise
            subprocess.run(
                ["sox", temp_audio_path, trimmed_audio_path, "trim", str(noise_start), str(noise_duration)],
                check=True
            )

            # 16. Mix the audio file with the overlay noise
            subprocess.run(
                ["sox", "-m", "-v", "1", audio_path, "-v", str(intensity), trimmed_audio_path, output_file],
                check=True,
                stderr=subprocess.DEVNULL
            )

            # 17. Remove the temporary trimmed audio file
            os.remove(trimmed_audio_path)

            if verbose:
                print(f"Added noise to {audio_path}")

        # 18. Remove the temporary audio file
        os.remove(temp_audio_path)


@timer
def add_noise(audio_paths, output_path, noise_type, intensity, ids, verbose):
    # 1. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)

    # 2. Select the noise type and add noise to the audio files
    match noise_type:
        case "video":
            add_video_noise(audio_paths, intensity, ids, output_path, verbose)
        case _:
            add_sox_noise(audio_paths, noise_type, intensity, output_path, verbose)

def main():
    parser = argparse.ArgumentParser(description="Add some noise to audio files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-o", "--output-path", default="data/noise/{noise_type}/{intensity}/", help="Output path for audio segments (default: data/noise/)")
    parser.add_argument("-n", "--noise-type", default="white", choices=["white", "pink", "brown", "red", "video"], help="Type of noise to add (default: white)")
    parser.add_argument("-y", "--ids", nargs="+", help="YouTube video IDs for custom noise")
    parser.add_argument("-i", "--intensity", type=float, default=1.0, help="Intensity of the noise (default: 1.0)")
    parser.add_argument("-v", "--verbose", action="store_true", help="Print verbose output", default=False)
    args = parser.parse_args()

    args.output_path = args.output_path.format(noise_type=args.noise_type, intensity=args.intensity)

    audio_paths = load_audio_files(args.paths)
        
    add_noise(audio_paths, args.output_path, args.noise_type, args.intensity, args.ids, args.verbose)

if __name__ == "__main__":
    main()
