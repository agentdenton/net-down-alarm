# Project: Net Down Alarm

## Project Overview

This project is a command-line utility named `net-down-alarm` that monitors a specified URL to check for internet connectivity. If the connection is down for a configurable number of attempts, it will play an alarm sound. The tool is written in Python and is designed to be cross-platform, with support for both Linux and Windows for audio playback and volume control.

The core technologies used are:
*   **Python:** The main programming language.
*   **Click:** For creating the command-line interface.
*   **requests:** For making HTTP requests to check for network connectivity.
*   **pycaw:** For audio control on Windows.
*   **amixer/paplay:** For audio control on Linux.

## Building and Running

This is a Python project and can be run from the command line.

### Installation

It is recommended to install the project dependencies in a virtual environment.

```bash
# Install python dependencies
pip install -e .

# Install node.js dependencies
npm install
```

### Running the application

The application is run using the `net-down-alarm` command, which is an entry point to the `cli` function in `main.py`.

```bash
net-down-alarm --file /path/to/your/alarm.mp3 --url https://www.google.com
```

### Command-line options

*   `--file` / `-f`: (Required) Path to the audio file to be played as an alarm.
*   `--volume` / `-v`: The volume level for the alarm (0-100). Defaults to 15.
*   `--url` / `-u`: The URL to monitor for connectivity. Defaults to `https://www.google.com`.
*   `--attempts` / `-a`: The number of failed connection attempts before the alarm is triggered. Defaults to 1.
*   `--period` / `-p`: The time in seconds between connection attempts. Defaults to 60.
*   `--loglevel` / `-l`: Set the log level (debug, info, warning, error, critical). Defaults to `info`.

## Development Conventions

*   The project uses `pyproject.toml` for Python project configuration and dependency management.
*   The code is structured with a main `cli` function that handles command-line arguments and a `main` function that contains the core application logic.
*   The application is designed to be cross-platform, with specific functions for handling audio on Windows and Linux.
