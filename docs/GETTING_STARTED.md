🇬🇧 English | 🇫🇷 [Français](GETTING_STARTED_FR.md) | 🇪🇸 [Español](GETTING_STARTED_ES.md)

# Getting Started (Raspberry Pi app, developer workspace setup)

This guide is for developers setting up a **local development environment** on their own machine
(Mac/Linux/Windows) to work on the ArcadeMatrix_RPi codebase - as opposed to `QUICKSTART.md`,
which targets end users flashing a pre-built image onto a Raspberry Pi. For architecture and
contribution conventions (Engines vs. Renderers), see `DEVELOPER.md` and `../CONTRIBUTING.md`.

## 1. Create a virtual environment

```bash
git clone <this-repo-url>
cd ArcadeMatrix_RPi
python3 -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
```

## 2. Install dependencies

```bash
pip install -r requirements.txt
pip install pytest                # not in requirements.txt (runtime deps only) - needed for tests
```

**Important hardware caveat**: `requirements.txt` does **not** include `rgbmatrix` - that's
[hzeller's `rpi-rgb-led-matrix`](https://github.com/hzeller/rpi-rgb-led-matrix) Python binding, a
compiled C++ extension that only builds/runs on real Raspberry Pi hardware (it talks directly to
the GPIO pins). This means:
- `python3 main.py` **cannot run end-to-end on a regular dev machine** - `core/matrix.py` imports
  `rgbmatrix` unconditionally at module load time, so it will fail immediately off-Pi.
- You *can* still develop and test everything that doesn't need to draw to a physical panel: the
  Flask API (`api/server.py`), config parsing (`core/config.py`), rotation logic
  (`core/rotation.py`), and most Engine business logic - see the testing section below, which
  already mocks the matrix layer entirely.
- If you want a live visual preview on your dev machine without a Pi, look at
  [`RGBMatrixEmulator`](https://github.com/ty-porter/RGBMatrixEmulator) (a drop-in, API-compatible
  package that renders to a Pygame window or browser instead of real GPIO). It is **not currently
  wired into this project** - `core/matrix.py` would need its `from rgbmatrix import ...` swapped
  conditionally - but it's a well-known compatible shim if you want to experiment with one locally.

## 3. Running the app for real

Actually running the full app requires a Raspberry Pi with the matrix wired per
`ARCHITECTURE.md`/the HAT vendor's instructions, and `rgbmatrix` compiled/installed
(`install.sh` at the repo root automates this, including the systemd service setup). On the Pi:

```bash
sudo python3 main.py
```

(root/`sudo` is required - `rgbmatrix` needs direct GPIO/DMA access.)

For a fully turnkey install, `install.sh` sets up an `arcadematrix.service` systemd unit so the
app starts on boot and restarts on crash - check its status/logs with:

```bash
sudo systemctl status arcadematrix.service
sudo journalctl -u arcadematrix.service -f      # live-tail systemd's own logs
```

## 4. Where the logs are

Independent of systemd, the app also writes its own rotating log file next to `main.py`:

```bash
tail -f arcadematrix.log            # rotates at 5MB, keeps 3 backups (see main.py)
```

A separate `crash.log` is written (overwritten) if the process dies from an uncaught exception
(see the `sys.excepthook` handler at the top of `main.py`) - check this first after any crash.

## 5. Running the test suite

This is the primary way to validate changes without needing real hardware - the existing suite
already mocks the matrix (`tests/conftest.py`'s `MockMatrix`/`MockMatrixWrapper`) so it runs
identically on your dev machine or in CI:

```bash
python3 -m pytest tests/ -v
```

See `DEVELOPER.md`'s "Testing Your Code" section for the project's coverage expectations
(100% on API routes) and `../CONTRIBUTING.md` for what counts as an Engine vs. a Renderer when adding
new test cases.

## 6. Building a release image (optional, for maintainers)

If you need to produce a full flashable Raspberry Pi OS image (like the one linked from
`QUICKSTART.md`), see `scripts/build_image.sh` (macOS/Linux, requires Docker) - it downloads
Raspberry Pi OS Lite, injects this repo, compiles the Python to bytecode to hide source, and
creates the FAT32/exFAT `DATA` partition end users drop their GIFs/fonts/sprites onto. This is a
10-15 minute process and not needed for day-to-day feature development - only for cutting a new
release artifact.

## Troubleshooting

- **`ModuleNotFoundError: No module named 'rgbmatrix'`** when running `python3 main.py` off-Pi:
  expected, see §2 above - use `pytest` for local development instead.
- **`ImportError` for `paho.mqtt`**: MQTT support is optional (`MQTT_AVAILABLE` flag in `main.py`);
  install `paho-mqtt` (already in `requirements.txt`) if you need to test Batocera/Recalbox
  integration locally.
- **Tests fail with `rgbmatrix` import errors**: make sure you're testing through `api/server.py`
  and the provided fixtures (`tests/conftest.py`) rather than importing `core.matrix` directly in
  a new test - the existing tests are structured specifically to avoid ever touching that module.
