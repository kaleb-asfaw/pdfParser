# pdfParser

## Overview

Converts boring school readings into summaries and audio files

## Installation

To get started with this project, follow these steps:

### Prerequisites

- **Operating System**: This script supports Linux and macOS. For Windows, please follow manual installation instructions below.
- **Shell**: Ensure you are using a shell that supports bash scripts.

### Automatic Installation (Linux/macOS)

1. **Clone the Repository**:

   ```bash
   git clone https://github.com/yourusername/yourrepository.git
   cd yourrepository

2. **Run the Setup Script**
   ```bash
   chmod +x setup.sh
  ./setup.sh

### Manual Installation
**For Linux-based Systems:**

Install System Dependencies:

1. **For Debian-based systems (Ubuntu):**

   ```bash
   Copy code
   sudo apt update
   sudo apt install portaudio19-dev python3-dev

2. **For Red Hat-based systems (Fedora):**

   ```bash
   Copy code
   sudo dnf install portaudio-devel python3-devel

**For macOS:**

Install System Dependencies:

   ```bash
   Copy code
   brew install portaudio
   ```
**For Windows:**

Install Python Dependencies:

   ```bash
   Copy code
   pip install -r requirements.txt
   Note: Windows users usually do not need to manually install PortAudio. Ensure you have the latest versions of pip, setuptools, and wheel:

   ```bash
   Copy code
   pip install --upgrade pip setuptools wheel

