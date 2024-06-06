# TAI3

sudo apt install sox

ffprobe -v error -show_entries stream=sample_rate,bits_per_sample,channels -of default=noprint_wrappers=1:nokey=1 "data/music/Beyoncé - TEXAS HOLD 'EM (Official Visualizer).wav"