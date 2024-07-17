#!/bin/bash

# Install system dependencies
if [ -x "$(command -v apt)" ]; then
    sudo apt update
    sudo apt install -y portaudio19-dev python3-dev
elif [ -x "$(command -v dnf)" ]; then
    sudo dnf install -y portaudio-devel python3-devel
elif [ -x "$(command -v brew)" ]; then
    brew install portaudio
else
    echo "Unsupported system. Please install PortAudio manually."
fi

# Install Python dependencies
pip install -r requirements.txt
