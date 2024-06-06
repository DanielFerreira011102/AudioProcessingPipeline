import os
import argparse
import subprocess

def load_audio_files(urls, file_paths):
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

def download_songs(urls, output_path, audio_format, sample_rate, bits_per_sample, channels):
    # 1. Check if the output path exists and create it if it does not
    os.makedirs(output_path, exist_ok=True)
    
    for url in urls:
        # 2. Download audio from YouTube
        subprocess.run(
            [
                'yt-dlp',
                '--format', 'bestaudio/best',
                '--output', f'{output_path}/%(title)s.%(ext)s',
                '--extract-audio',
                '--audio-format', audio_format,
                '--audio-quality', '192',
                '--postprocessor-args', f'ffmpeg:-ar {sample_rate} -ac {channels} -sample_fmt s{bits_per_sample}',
                url
            ],
            check=True
        )

        print(f"Downloaded audio from {url}")

def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube playlists and individual videos.")
    parser.add_argument("urls", nargs="*", help="YouTube playlist URLs and/or individual video URLs")
    parser.add_argument("-o", "--output-path", default="data/music", help="Output path for the downloaded audio files (default: data/music/)")
    parser.add_argument("-f", "--file-paths", nargs="+", help="File containing YouTube playlist URLs and/or individual video URLs, one per line")
    parser.add_argument("-x", "--audio-format", choices=["mp3", "wav"], default="wav", help="Audio format for downloaded files (default: wav)")
    parser.add_argument("-r", "--sample-rate", type=int, default=44100, help="Sample rate for downloaded audio files (default: 44100)")
    parser.add_argument("-b", "--bits-per-sample", type=int, default=16, help="Bits per sample for downloaded audio files (default: 16)")
    parser.add_argument("-c", "--channels", type=int, default=2, help="Number of channels for downloaded audio files (default: 2)")
    args = parser.parse_args()
    
    urls = load_audio_files(args.urls, args.file_paths)

    download_songs(urls, args.output_path, args.audio_format, args.sample_rate, args.bits_per_sample, args.channels)

if __name__ == "__main__":
    main()
