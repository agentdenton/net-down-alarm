## Install

### Install locally, editable

```bash
git clone https://github.com/agentdenton/net-down-alarm
cd net-down-alarm
uv venv
uv pip install -e .
```

### Install globally with pipx

```bash
# Ensure pipx is in your PATH
pipx ensurepath
pipx install .
```

## Run

```bash
net-down-alarm --file /path/to/your/alarm.mp3 -a 3 -p 60 -v 20
```

## Make an exe

```bash
uv add --dev pyinstaller
uv run pyinstaller --onefile main.py --name net-down-alarm
```
