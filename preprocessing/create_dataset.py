import os
import argparse
import yt_dlp

def download_songs(urls, output_path, audio_format, sample_rate):
    os.makedirs(output_path, exist_ok=True)
    
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': os.path.join(output_path, '%(title)s.%(ext)s'),
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': audio_format,
            'preferredquality': '192',
        }],
        'postprocessor_args': [
            '-ar', str(sample_rate),
        ],
        'quiet': True,
        'extract_flat': False,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        for url in urls:
            info = ydl.extract_info(url, download=True)

            if not 'entries' in info and not 'title' in info:
                print(f"Failed to download: {url}")
                continue

            if 'title' in info:
                print(f"Downloaded: {info['title']}")
                
            if 'entries' in info:
                for entry in info['entries']:
                    print(f"Downloaded: {entry['title']}")

def main():
    parser = argparse.ArgumentParser(description="Download audio from YouTube playlists and individual videos.")
    parser.add_argument("urls", nargs="*", help="YouTube playlist URLs and/or individual video URLs")
    parser.add_argument("-o", "--output-path", default="data/", help="Output path for the downloaded audio files (default: data/music/)")
    parser.add_argument("-f", "--file-path", help="File containing YouTube playlist URLs and/or individual video URLs, one per line")
    parser.add_argument("-x", "--audio-format", choices=["mp3", "wav"], default="mp3", help="Audio format for downloaded files (default: mp3)")
    parser.add_argument("-r", "--sample-rate", type=int, default=44100, help="Sample rate for downloaded audio files (default: 44100)")
    args = parser.parse_args()
    
    urls = args.urls
    
    if args.file_path:
        with open(args.file_path, 'r') as file:
            urls.extend(line.strip() for line in file if line.strip())

    if not urls:
        print("No URLs provided")
        return

    download_songs(urls, args.output_path, args.audio_format, args.sample_rate)

if __name__ == "__main__":
    main()
