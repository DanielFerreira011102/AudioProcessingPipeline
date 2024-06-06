#!/bin/bash

# Function to check if a package is installed
check_package() {
    if dpkg -l | grep -q $1; then
        echo "$1 is already installed."
    else
        echo "$1 is not installed. Installing $1..."
        sudo apt-get install -y $1
    fi
}

# Check and install each package
check_package sox
check_package yt-dlp
check_package fftw3
check_package fftw3-dev
check_package pkg-config
check_package libsndfile1-dev

# Install Python requirements
echo "Installing Python requirements..."
pip install -r requirements.txt

# Install current directory as a package
echo "Installing current directory as a package..."
pip install -e .