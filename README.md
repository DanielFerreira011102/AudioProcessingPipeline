# TAI3

sudo apt install sox

1. python3 preprocessing/create_dataset.py -f data/playlists.txt -o data/music -x wav

2. python3 preprocessing/create_signatures.py data/music

3. python3 preprocessing/create_compression_results.py data/signatures -x gzip

4. python3 preprocessing/create_audio_segment.py data/music -d 5 -m 60

5. python3 preprocessing/create_signatures.py data/segments -o data/segments_signatures

6. python3 src/main.py data/segments_signatures -s data/signatures -y data/compression_results/gzip/results.csv -x gzip

ffprobe -v error -show_entries stream=sample_rate,bits_per_sample,channels -of default=noprint_wrappers=1:nokey=1 "data/music/Beyoncé - TEXAS HOLD 'EM (Official Visualizer).wav"