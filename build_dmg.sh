#!/bin/bash
# Build DMG for OSCUsend distribution

set -e

APP_NAME="OSCUsend"
VERSION="1.0.0"
DMG_NAME="${APP_NAME}-${VERSION}.dmg"
VOL_NAME="${APP_NAME}"
SOURCE_DIR="dist"
APP_FILE="${SOURCE_DIR}/${APP_NAME}"
DMG_TEMP="dmg_temp"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Building DMG for ${APP_NAME} ${VERSION}${NC}"

# Check if app exists
if [ ! -f "${APP_FILE}" ]; then
    echo -e "${RED}Error: ${APP_FILE} not found. Run pyinstaller first:${NC}"
    echo "  pyinstaller --onefile --name OSCUsend src/oscusend.py"
    exit 1
fi

# Clean up previous builds
echo "Cleaning up previous builds..."
rm -f "${DMG_NAME}"
rm -rf "${DMG_TEMP}"

# Create temporary DMG directory
mkdir -p "${DMG_TEMP}"

# Copy app to temp directory
echo "Copying app to temp directory..."
cp -R "${APP_FILE}" "${DMG_TEMP}/"

# Create a symlink to Applications folder for easy installation
ln -s /Applications "${DMG_TEMP}/Applications"

# Create README in DMG
cat > "${DMG_TEMP}/README.txt" << 'EOF'
OSCUsend - Global Hotkey to OSC Message Converter

INSTALLATION:
  Drag OSCUsend to the Applications folder

FIRST RUN - GRANT PERMISSIONS:
  1. Open System Settings → Privacy & Security → Accessibility
  2. Click the lock and enter your password
  3. Add "OSCUsend" and enable it
  4. (Optional) Do the same for Input Monitoring if prompted

USAGE:
  Double-click OSCUsend to use default configuration:
    Hotkey: Cmd+F15
    Destinations: 10.10.20.101:5000, 10.10.20.102:5000
    OSC Path: /millumin/action/launchNextColumn
    Value: next

  Or run from Terminal with custom arguments:
    /Applications/OSCUsend -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next

  Press Ctrl+C to quit.

For more information: https://github.com/alokw/oscusend
EOF

# Create DMG
echo "Creating DMG..."
hdiutil create -volname "${VOL_NAME}" \
               -srcfolder "${DMG_TEMP}" \
               -ov \
               -format UDZO \
               "${DMG_NAME}"

# Clean up temp directory
rm -rf "${DMG_TEMP}"

echo -e "${GREEN}Done! Created ${DMG_NAME}${NC}"
ls -lh "${DMG_NAME}"
