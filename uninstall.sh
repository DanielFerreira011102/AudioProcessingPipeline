#!/bin/bash

# Function to check if a package is installed and remove it
remove_package() {
    if dpkg -l | grep -q $1; then
        echo "Removing $1..."
        sudo apt-get remove -y $1
    else
        echo "$1 is not installed."
    fi
}

# Remove each package
remove_package sox
remove_package yt-dlp
remove_package fftw3
remove_package fftw3-dev
remove_package pkg-config
remove_package libsndfile1-dev

# Remove Python requirements
echo "Removing Python requirements..."
pip uninstall -r requirements.txt -y

# Uninstall current directory package
echo "Uninstalling current directory package..."
pip uninstall -y $(basename $(pwd))

echo "Uninstallation complete."