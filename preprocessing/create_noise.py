import os
import argparse
import numpy as np
import matplotlib.pyplot as plt
import yt_dlp
from pydub import AudioSegment

def white_noise(N, intensity, x=None, state=None):
    state = np.random.RandomState() if state is None else state
    y = state.randn(N)
    x = 1.0 if x is None else (np.abs(x.get_array_of_samples()) ** 2.0).mean()
    y = y * np.sqrt(x / (np.abs(y)**2.0).mean())
    y = (y * intensity).astype(np.int16)
    return y

def pink_noise(N, intensity, x=None, state=None):
    state = np.random.RandomState() if state is None else state
    uneven = N % 2
    X = state.randn(N // 2 + 1 + uneven) + 1j * state.randn(N // 2 + 1 + uneven)
    S = np.sqrt(np.arange(len(X)) + 1.0)
    y = (np.fft.irfft(X / S)).real
    if uneven:
        y = y[:-1]
    x = 1.0 if x is None else (np.abs(x.get_array_of_samples()) ** 2.0).mean()
    y = y * np.sqrt(x / (np.abs(y)**2.0).mean())
    y = (y * intensity).astype(np.int16)
    return y

def brown_noise(N, intensity, x=None, state=None):
    state = np.random.RandomState() if state is None else state
    uneven = N % 2
    X = state.randn(N // 2 + 1 + uneven) + 1j * state.randn(N // 2 + 1 + uneven)
    S = (np.arange(len(X)) + 1.0)
    y = (np.fft.irfft(X * S)).real
    if uneven:
        y = y[:-1]
    x = 1.0 if x is None else (np.abs(x.get_array_of_samples()) ** 2.0).mean()
    y = y * np.sqrt(x / (np.abs(y)**2.0).mean())
    y = (y * intensity).astype(np.int16)
    return y


def video_noise(ids, N, intensity, x, audio_format="wav", sample_rate=44100):
    id_ = np.random.choice(ids)

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'cache/%(id)s.%(ext)s',
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

        if not os.path.exists(f"cache/{id_}.wav"):
            info = ydl.extract_info(f"https://www.youtube.com/watch?v={id_}", download=True)

            if not 'title' in info:
                print(f"Failed to download: {id_}")
                return
                    
            print(f"Downloaded: {info['title']}")

    y = AudioSegment.from_file(f"cache/{id_}.wav")

    y = y.set_sample_width(x.sample_width)
    y = y.set_frame_rate(x.frame_rate)
    y = y.set_channels(x.channels)

    y = np.array(y.get_array_of_samples())
    y_start = np.random.randint(0, len(y) - N)
    y = y[y_start:y_start + N]

    x_max = np.abs(x.get_array_of_samples()).max()
    y_max = np.abs(y).max()
    intensity = intensity * x_max / y_max

    y = (y * intensity).astype(np.int16)
    return y

def add_noise(audio_paths, output_path, noise_type, intensity, ids):
    os.makedirs(output_path, exist_ok=True)

    for audio_path in audio_paths:
        audio_format = audio_path.rsplit('.', 1)[1]

        audio = AudioSegment.from_file(audio_path)

        N = len(audio.get_array_of_samples())

        match noise_type:
            case "white":
                noise = white_noise(N, intensity, audio)
            case "pink":
                noise = pink_noise(N, intensity, audio)
            case "brown" | "brownian" | "red":
                noise = brown_noise(N, intensity, audio)
            case "video":
                noise = video_noise(ids, N, intensity, audio)
            case _:
                print(f"Invalid noise type: {noise_type}")
                return

        noisy_audio = audio.overlay(AudioSegment(noise.tobytes(), frame_rate=audio.frame_rate, sample_width=audio.sample_width, channels=audio.channels), loop=True)

        output_file = os.path.join(output_path, f"{os.path.basename(audio_path).rsplit('.', 1)[0]}_{noise_type}_{intensity}.{audio_format}")

        noisy_audio.export(output_file, format=audio_format)
        print(f"Added noise to: {output_file}")

def main():
    parser = argparse.ArgumentParser(description="Add some noise to audio files.")
    parser.add_argument("paths", nargs="+", help="Path to audio files or directories containing audio files")
    parser.add_argument("-o", "--output-path", default="data/noise/", help="Output path for audio segments (default: data/noise/)")
    parser.add_argument("-n", "--noise-type", default="white", help="Type of noise to add (default: white)")
    parser.add_argument("-y", "--ids", nargs="+", help="YouTube video IDs for custom noise")
    parser.add_argument("-i", "--intensity", type=float, default=1.0, help="Intensity of the noise (default: 1.0)")
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
    
    if args.noise_type == "video" and not args.ids:
        print("No video IDs provided")
        return
        
    add_noise(audio_paths, args.output_path, args.noise_type, args.intensity, args.ids)

if __name__ == "__main__":
    main()