#!/bin/bash

echo "Installing FFmpeg for Linux..."

# Create ffmpeg directory if it doesn't exist
mkdir -p ffmpeg

# Download FFmpeg
wget https://johnvansickle.com/ffmpeg/releases/ffmpeg-release-amd64-static.tar.xz

# Extract FFmpeg
tar xf ffmpeg-release-amd64-static.tar.xz

# Move FFmpeg files to the correct location
mv ffmpeg-*-amd64-static/ffmpeg ffmpeg/
mv ffmpeg-*-amd64-static/ffprobe ffmpeg/

# Clean up
rm -rf ffmpeg-*-amd64-static
rm ffmpeg-release-amd64-static.tar.xz

# Make FFmpeg executable
chmod +x ffmpeg/ffmpeg
chmod +x ffmpeg/ffprobe

echo "FFmpeg installation completed!"
echo "FFmpeg is now available in the ffmpeg directory" 