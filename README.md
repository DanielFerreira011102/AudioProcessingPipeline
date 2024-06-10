# TAI3: Audio Processing Pipeline

---

## Table of Contents

1. [Overview](#overview)
2. [Requirements](#requirements)
3. [Installation](#installation)
4. [Running the Pipeline](#running-the-pipeline)
5. [Configuration](#configuration)
6. [Project Structure](#project-structure)
7. [Report](#report)
8. [Video](#video)

---

## Overview

This project provides a comprehensive audio processing pipeline designed to automate tasks such as creating audio datasets, generating noise segments, and computing audio signatures for analysis. It leverages Python for script orchestration and a variety of tools for audio processing.

## Requirements

Before you can use this pipeline, ensure you have the following:

- **Operating System:** Linux-based (Ubuntu recommended)
- **Python:** Version 3.8 or higher
- **Packages:** Listed in `requirements.txt`
- **System Tools:** 
  - `sox`
  - `yt-dlp`
  - `fftw3`
  - `fftw3-dev`
  - `pkg-config`
  - `libsndfile1-dev`

## Installation

Follow these steps to set up the project:

1. **Clone the Repository:**

   ```bash
   git clone git@github.com:DanielFerreira011102/TAI3.git
   cd TAI3
    ```
2. Install Required Packages:

    Run the provided installation script to ensure all dependencies are installed.

    ```bash
    ./src/bash/install.sh
    ```

    This script performs the following:

    - Checks for and installs necessary system packages.
    - Installs Python dependencies from requirements.txt.
    - Installs the current directory as a Python package in editable mode.

## Running the Pipeline

To execute the audio processing pipeline:

1. Navigate to the Project Directory:

    ```bash
    cd TAI3
    ```

2. Run the Pipeline:

    Use the following command to start the pipeline with the provided configuration file:

    ```bash
    python3 src/pipeline.py src/pipelines/sample_config.yaml
    ```

    This will sequentially execute all the steps defined in the configuration file.

## Configuration

he pipeline is controlled via a YAML configuration file (`sample_config.yaml`). Each step in the pipeline is defined with a script to run and associated arguments.

### Sample Configuration

Here's an example of a configuration file:

```yaml
steps:
  - script: src/preprocessing/create_dataset.py
    args:
      file_paths: ["data/playlists.txt"]
      output_path: "data/music"
      audio_format: "wav"
      sample_rate: 44100
      bits_per_sample: 16
      channels: 2
  - script: src/preprocessing/create_segments.py
    args:
      __NO_ARG_NAME__paths: ["data/music"]
      duration: 5
      min_time: 60
      start_time: null
      output_path: "data/segments"
  - script: src/preprocessing/create_noise.py
    args:
      __NO_ARG_NAME__paths: ["data/segments"]
      output_path: "data/noise"
      noise_type: "white"
      intensity: 0.3
  - script: src/preprocessing/create_signatures.py
    args:
      __NO_ARG_NAME__paths: ["data/music"]
      output_path: "data/signatures/original"
      signature-args: "-ws 1024 -sh 256 -nf 8"
      signature_type: "gmf"
  - script: src/preprocessing/create_signatures.py
    args:
      __NO_ARG_NAME__paths: ["data/noise"]
      output_path: "data/signatures/segments"
      signature_type: "gmf"
      signature_args: ""
  - script: src/main/create_distance_results.py
    args:
      __NO_ARG_NAME__paths: ["data/signatures/segments"]
      database_path: "data/signatures/original"
      algorithm: "bz2"
      output_path: "data/distances/{algorithm}/results.csv"
```
#### Key Components
- script: The Python script to run.
- args: Arguments for the script. Use `__NO_ARG_NAME__` for positional arguments.

## Project Structure

The project is organized as follows:

```plaintext
TAI3/
├── data/                          # Data directory
├── GetMaxFreqs/                   # External tool for audio processing
├── src/
│   ├── bash/
│   │   └── install.sh             # Installation script
│   ├── pipelines/
│   │   └── sample_config.yaml     # Sample pipeline configuration
│   ├── preprocessing/             # Preprocessing scripts
│   │   ├── create_dataset.py
│   │   ├── create_segments.py
│   │   ├── create_noise.py
│   │   └── create_signatures.py
│   ├── main/                      # Main processing scripts
│   │   └── create_distance_results.py
│   └── pipeline.py                # Pipeline orchestrator
└── README.md                      # This README file
```

## Report
The report for this project can be found [here](report.pdf).

## Video
The video presentation for this project can be found [here](...).