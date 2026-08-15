# ArcadeMatrix Music Sender

This tool captures now-playing information from audio players on Windows and exposes it via HTTP for display on the ArcadeMatrix_RPI LED matrix.

## Features

- **Native Player Support**: Detects playing tracks from VLC, Spotify Desktop, Foobar2000, and other native audio players using pycaw
- **Web Player Support**: Works with web players like Deezer, Spotify Web, YouTube Music via browser extension
- **HTTP API**: Exposes current track info at `GET /nowplaying` and accepts updates via `POST /nowplaying`
- **Windows Only**: Uses Windows-specific APIs (pycaw)

## Installation

1. Install Python dependencies:
   ```
   pip install -r requirements.txt
   ```

2. Run the tool:
   ```
   python music_sender.py --port 8085
   ```

3. For web player support, install the browser extension in Chrome/Firefox

## Usage

### Command Line Options
- `--port` or `-p`: Port to listen on (default: 8085)

### API Endpoints
- `GET /nowplaying`: Returns current track information as JSON
- `POST /nowplaying`: Accepts track data from browser extension
- `GET /health`: Returns server health status

## Configuration

1. Run the tool on your Windows PC
2. Configure the RPI to connect to your PC's IP and port (default: `http://192.168.1.100:8085`)
3. For web players, install the browser extension and configure it with your PC's IP address

## Files

```
tools/music_sender/
├── music_sender.py        # Main Python script
├── requirements.txt       # Python dependencies
├── start_sender.bat       # Windows startup script
├── README.md              # This file
└── extension/             # Browser extension files
    ├── manifest.json      # Extension manifest
    ├── background.js      # Background script
    ├── popup.html         # Configuration popup
    └── popup.js           # Popup logic
```

## Requirements

- Python 3.x
- Windows OS (pycaw only works on Windows)
- pycaw library (`pip install pycaw`)
- comtypes library (`pip install comtypes`)

## Browser Extension

The browser extension supports:
- Spotify Web Player
- Deezer Web Player  
- YouTube Music

Install the extension in Chrome/Firefox and configure it with your PC's IP address to send now-playing data to the music_sender tool.

## Troubleshooting

### "pycaw not available" error
This tool requires Windows and pycaw to detect native audio players. If you're on a non-Windows system, only web player support will work.

### Connection issues
1. Ensure the PC running `music_sender.py` is reachable from your RPI
2. Check that the port (default 8085) is open and not blocked by firewall
3. Verify the IP address in the browser extension configuration matches your PC's IP

### Web player detection
If web player detection isn't working:
1. Make sure you've installed the browser extension
2. Ensure the extension has permission to access tabs
3. Check that the IP address in the extension popup is correct
4. Test connection from the extension popup