# OSCUsend

A simple macOS application that listens for a global hotkey and sends OSC messages to two configurable destinations. Runs in the background and works even when the app is not active.

## Features

- Global hotkey monitoring (works when app is in background)
- Sends OSC messages to two configurable destinations
- Command-line interface (works consistently between script and .app)
- Runs as background agent (no dock icon when bundled as .app)
- Console logging for debugging

## Requirements

- macOS 10.15+ (Catalina or later recommended)
- Python 3.8+

## Installation

### Option 1: Run as Python Script

1. Clone this repository:
```bash
git clone <repository-url>
cd oscusend
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Run with command-line arguments:
```bash
python src/oscusend.py -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next
```

### Option 2: Bundle as macOS .app

1. Install PyInstaller:
```bash
pip install pyinstaller
```

2. Build the app:
```bash
pyinstaller --onefile --name OSCUsend src/oscusend.py
```

3. Move to Applications folder:
```bash
mv dist/OSCUsend /Applications/
```

4. Grant permissions (see [macOS Privacy & Security](#macos-privacy--security-settings) below)

5. Run it:
```bash
# Double-click in Applications, or from terminal:
/Applications/OSCUsend -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next
```

**Optional: Create distributable DMG**
```bash
./build_dmg.sh
```

**Optional: Install convenience wrapper** (lets you run `oscusend` from anywhere):
```bash
sudo cp oscusend /usr/local/bin/
```

Then use:
```bash
oscusend -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next
```

## Configuration

All configuration is done via command-line arguments (same for both script and .app):

```bash
python src/oscusend.py [OPTIONS]
# or
/Applications/OSCUsend.app/Contents/MacOS/OSCUsend [OPTIONS]
```

| Argument | Required | Default | Description |
|----------|----------|---------|-------------|
| `-hotkey` | No | `cmd+f15` | Hotkey combination (e.g., `cmd+f15`, `ctrl+shift+a`) |
| `-dest1` | No | `10.10.20.101:5000` | First OSC destination as `IP:PORT` |
| `-dest2` | No | `10.10.20.102:5000` | Second OSC destination as `IP:PORT` |
| `-oscpath` | No | `/millumin/action/launchNextColumn` | OSC path to send to |
| `-oscval` | No | `next` | OSC value to send (string) |

**All arguments are optional** - run without any arguments to use defaults.

### Default Configuration

If run without arguments, the app uses these defaults:
- Hotkey: `cmd+f15`
- Destination 1: `10.10.20.101:5000` → `/millumin/action/launchNextColumn` with value `next`
- Destination 2: `10.10.20.102:5000` → `/millumin/action/launchNextColumn` with value `next`

**To change defaults**, edit the variables at the top of `src/oscusend.py`:

```python
# =============================================================================
# DEFAULTS - Modify these to change default behavior
# =============================================================================

DEFAULT_HOTKEY = 'cmd+f15'
DEFAULT_DEST1_IP = '10.10.20.101'
DEFAULT_DEST1_PORT = 5000
DEFAULT_DEST2_IP = '10.10.20.102'
DEFAULT_DEST2_PORT = 5000
DEFAULT_OSC_PATH = '/millumin/action/launchNextColumn'
DEFAULT_OSC_VALUE = 'next'
DEFAULT_TRIGGER_COOLDOWN = 0.2  # seconds
```

### Hotkey Examples

- `cmd+f15` - Command + F15
- `cmd+shift+a` - Command + Shift + A
- `ctrl+option+f1` - Control + Option + F1
- `cmd+space` - Command + Space (may conflict with Spotlight)

## macOS Privacy & Security Settings

**IMPORTANT**: macOS requires TWO separate permissions for apps that monitor global keyboard input.

### 1. Accessibility Permission (Required)

Global hotkey monitoring requires Accessibility permission.

1. Open **System Settings** (or System Preferences on older macOS)
2. Go to **Privacy & Security** → **Accessibility**
3. Click the lock icon and enter your password
4. Add **Terminal** (if running as script) or **OSCUsend** (if running as .app)
5. Enable the checkbox next to it
6. **Restart the app** after granting permission

### 2. Input Monitoring Permission (May Be Required)

Some macOS versions may also require Input Monitoring permission.

1. Open **System Settings** → **Privacy & Security** → **Input Monitoring**
2. Click the lock icon and enter your password
3. Add **Terminal** (if running as script) or **OSCUsend** (if running as .app)
4. Enable the checkbox next to it
5. **Restart the app** after granting permission

### Which App to Add?

- **Running as script**: Add **Terminal** from `/Applications/Utilities/`
- **Running as .app bundle**: Add **OSCUsend** from your Applications folder

### Troubleshooting

If hotkey doesn't work:
- Verify **both** Accessibility and Input Monitoring permissions are granted
- Check that the hotkey doesn't conflict with system shortcuts
- Review console logs for errors
- Try a different hotkey combination
- Make sure to restart the app after granting permissions

## Usage

Once running, OSCUsend will:
- Log the configured OSC destinations
- Listen for your configured hotkey
- Send OSC messages to both destinations when the hotkey is pressed
- Log each OSC message sent

Example console output:
```
2026-05-18 10:30:00 - OSCUSend - INFO - OSC destination configured: 10.10.20.101:5000 → /millumin/action/launchNextColumn
2026-05-18 10:30:00 - OSCUSend - INFO - OSC destination configured: 10.10.20.102:5000 → /millumin/action/launchNextColumn
2026-05-18 10:30:00 - OSCUSend - INFO - Starting OSCSend...
2026-05-18 10:30:00 - OSCUSend - INFO - Listening for hotkey: cmd+f15
2026-05-18 10:30:00 - OSCUSend - INFO - Press Ctrl+C to quit
2026-05-18 10:30:15 - OSCUSend - INFO - Hotkey 'cmd+f15' pressed
2026-05-18 10:30:15 - OSCUSend - INFO - OSC sent: 10.10.20.101:5000 → /millumin/action/launchNextColumn = 'next'
2026-05-18 10:30:15 - OSCUSend - INFO - OSC sent: 10.10.20.102:5000 → /millumin/action/launchNextColumn = 'next'
```

## Testing OSC Reception

To test that OSC messages are being sent correctly, you can use an OSC debugger like:
- [OSC Monitor](https://github.com/SofaPirate/OSCMonitor)
- [TouchOSC Editor](https://hexler.net/touchosc)
- Simple Python listener:
```python
from pythonosc import dispatcher, osc_server
# Run on port matching your destination
```

## License

MIT
