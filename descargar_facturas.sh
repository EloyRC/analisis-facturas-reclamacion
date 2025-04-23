#!/bin/bash

# Set your Google Drive file ID and desired output name
FILE_ID="1oZ3DGyBcVXPUWRdFUcZ7bv2rIAqQdHbb"
OUTPUT_ZIP="downloaded.zip"

# Download the ZIP file using gdown
gdown "https://drive.google.com/uc?id=${FILE_ID}&export=download" -O "${OUTPUT_ZIP}"

# Unzip the downloaded file to the current directory
unzip "${OUTPUT_ZIP}"

# Optionally, remove the ZIP file after extraction
rm "${OUTPUT_ZIP}"