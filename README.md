# OSCUsend

A simple macOS application that listens for a global hotkey and sends OSC messages to two configurable destinations. Runs in the background and works even when the app is not active.

## Features

- Global hotkey monitoring (works when app is in background)
- Sends OSC messages to two configurable destinations
- Simple `.env` file configuration
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

3. Copy the example environment file and configure:
```bash
cp .env.example .env
```

4. Edit `.env` with your settings (see [Configuration](#configuration)).

5. Run the app:
```bash
python src/oscusend.py
```

### Option 2: Bundle as macOS .app

1. Install py2app:
```bash
pip install py2app
```

2. Build the app bundle:
```bash
python setup.py py2app
```

3. The .app bundle will be created in `dist/OSCUsend.app`

4. Copy your `.env` file to the app bundle:
```bash
cp .env dist/OSCUsend.app/Contents/MacOS/.env
```

5. Move to Applications folder:
```bash
mv dist/OSCUsend.app /Applications/
```

## Configuration

Edit the `.env` file to configure your settings:

```bash
# Hotkey to trigger OSC messages
# Format: modifier+key
# Modifiers: cmd, ctrl, shift, option/alt
HOTKEY=cmd+f15

# OSC Destination 1
OSC_DEST1_IP=127.0.0.1
OSC_DEST1_PORT=8000
OSC_DEST1_PATH=/trigger
OSC_DEST1_VALUE=activate

# OSC Destination 2
OSC_DEST2_IP=127.0.0.1
OSC_DEST2_PORT=8001
OSC_DEST2_PATH=/trigger
OSC_DEST2_VALUE=activate
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

- **Running as script (`python src/oscusend.py`)**: Add **Terminal** from `/Applications/Utilities/`
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
2025-01-18 10:30:00 - OSCUSend - INFO - OSC destination configured: 127.0.0.1:8000/trigger
2025-01-18 10:30:00 - OSCUSend - INFO - OSC destination configured: 127.0.0.1:8001/trigger
2025-01-18 10:30:00 - OSCUSend - INFO - Starting OSCSend...
2025-01-18 10:30:00 - OSCUSend - INFO - Listening for hotkey: cmd+f15
2025-01-18 10:30:00 - OSCUSend - INFO - Press Ctrl+C to quit
2025-01-18 10:30:15 - OSCUSend - INFO - Hotkey 'cmd+f15' pressed
2025-01-18 10:30:15 - OSCUSend - INFO - OSC sent: 127.0.0.1:8000/trigger = 'activate'
2025-01-18 10:30:15 - OSCUSend - INFO - OSC sent: 127.0.0.1:8001/trigger = 'activate'
```

## Testing OSC Reception

To test that OSC messages are being sent correctly, you can use an OSC debugger like:
- [OSC Monitor](https://github.com/SofaPirate/OSCMonitor)
- [TouchOSC Editor](https://hexler.net/touchosc)
- Simple Python listener:
```python
from pythonosc import dispatcher, osc_server
# Run on port 8000 to receive test messages
```

## License

MIT
