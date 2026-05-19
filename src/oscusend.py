#!/usr/bin/env python3
"""
OSCSend - Global hotkey to OSC message converter for macOS

Usage:
  python src/oscusend.py -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next
"""

import argparse
import logging
import sys
import time
from dataclasses import dataclass

from pynput import keyboard
from pythonosc import udp_client

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
DEFAULT_TRIGGER_COOLDOWN = 0.2  # seconds (prevents duplicate triggers)

# =============================================================================

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('OSCUSend')


@dataclass
class OSCDestination:
    """OSC destination configuration"""
    ip: str
    port: int
    path: str
    value: str


class OSCSendApp:
    """Main application class"""

    def __init__(self, args=None):
        self.osc_clients = []  # List of (client, destination) tuples
        self.last_trigger_time = 0
        self.trigger_cooldown = DEFAULT_TRIGGER_COOLDOWN
        self.hotkey_listener = None

        self.config = self._load_config(args)
        self._setup_osc_clients()

    def _load_config(self, args) -> dict:
        """Load configuration from args or defaults"""
        config = {}

        if args.dest1:
            # Use provided arguments
            hotkey_str = args.hotkey.lower()
            config['dest1'] = self._parse_destination(args.dest1, args.oscpath, args.oscval)
            config['dest2'] = self._parse_destination(args.dest2, args.oscpath, args.oscval) if args.dest2 else None
        else:
            # Use defaults when run without arguments
            logger.info("No arguments provided. Using default configuration.")
            logger.info("Run with --help for usage options.")
            hotkey_str = DEFAULT_HOTKEY
            config['dest1'] = OSCDestination(ip=DEFAULT_DEST1_IP, port=DEFAULT_DEST1_PORT, path=DEFAULT_OSC_PATH, value=DEFAULT_OSC_VALUE)
            config['dest2'] = None
            if DEFAULT_DEST2_IP:
                config['dest2'] = OSCDestination(ip=DEFAULT_DEST2_IP, port=DEFAULT_DEST2_PORT, path=DEFAULT_OSC_PATH, value=DEFAULT_OSC_VALUE)

        config['hotkey'] = self._parse_hotkey(hotkey_str)
        return config

    def _parse_destination(self, dest_str, oscpath, oscval):
        """Parse destination string 'ip:port' and combine with shared OSC path/value"""
        if ':' in dest_str:
            ip, port = dest_str.split(':', 1)
        else:
            ip = dest_str
            port = 8000
        return OSCDestination(ip=ip, port=int(port), path=oscpath, value=oscval)

    def _parse_hotkey(self, hotkey_str: str) -> dict:
        """Parse hotkey string into pynput format"""
        parts = hotkey_str.split('+')

        # Map modifier strings to pynput format
        # Modifiers and function keys need to be wrapped in <>
        modifier_map = {
            'cmd': '<cmd>',
            'command': '<cmd>',
            'ctrl': '<ctrl>',
            'control': '<ctrl>',
            'shift': '<shift>',
            'option': '<alt>',
            'alt': '<alt>',
        }

        formatted_parts = []

        for part in parts:
            part = part.strip().lower()
            if part in modifier_map:
                formatted_parts.append(modifier_map[part])
            elif part.startswith('f') and part[1:].isdigit():
                # Function key (f1, f2, etc.) - wrap in <>
                formatted_parts.append(f'<{part}>')
            elif len(part) == 1:
                # Regular character key - don't wrap
                formatted_parts.append(part)
            else:
                logger.error(f"Invalid key: {part}")
                sys.exit(1)

        pynput_format = '+'.join(formatted_parts)

        return {
            'pynput_format': pynput_format,
            'original': hotkey_str
        }

    def _setup_osc_clients(self):
        """Setup OSC UDP clients for each destination"""
        dests = [self.config['dest1']]
        if self.config['dest2']:
            dests.append(self.config['dest2'])

        for dest in dests:
            client = udp_client.SimpleUDPClient(dest.ip, dest.port)
            self.osc_clients.append((client, dest))
            logger.info(f"OSC destination configured: {dest.ip}:{dest.port} → {dest.path}")

    def _send_osc_messages(self):
        """Send OSC messages to all configured destinations"""
        current_time = time.time()

        # Prevent duplicate triggers from key repeat
        if current_time - self.last_trigger_time < self.trigger_cooldown:
            return

        self.last_trigger_time = current_time

        for client, dest in self.osc_clients:
            try:
                client.send_message(dest.path, dest.value)
                logger.info(f"OSC sent: {dest.ip}:{dest.port} → {dest.path} = '{dest.value}'")
            except Exception as e:
                logger.error(f"Failed to send OSC to {dest.ip}:{dest.port}: {e}")

    def on_activate(self):
        """Callback when hotkey is pressed"""
        logger.info(f"Hotkey '{self.config['hotkey']['original']}' pressed")
        self._send_osc_messages()

    def start(self):
        """Start the hotkey listener"""
        hotkey = self.config['hotkey']

        # Create the hotkey - GlobalHotKeys uses string format like '<cmd>+<f15>'
        self.hotkey_listener = keyboard.GlobalHotKeys({
            hotkey['pynput_format']: self.on_activate
        })

        logger.info(f"Starting OSCSend...")
        logger.info(f"Listening for hotkey: {hotkey['original']}")
        logger.info("Press Ctrl+C to quit")

        try:
            self.hotkey_listener.start()
            self.hotkey_listener.join()
        except KeyboardInterrupt:
            logger.info("Shutting down...")
            if self.hotkey_listener:
                self.hotkey_listener.stop()


def parse_args():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description='Send OSC messages via global hotkey',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s -hotkey cmd+f15 -dest1 10.10.20.101:5000 -dest2 10.10.20.102:5000 -oscpath /millumin/action/launchNextColumn -oscval next
  %(prog)s -hotkey ctrl+shift+a -dest1 127.0.0.1:8000
        """
    )

    parser.add_argument('-hotkey', default=DEFAULT_HOTKEY,
                        help=f'Hotkey combination (e.g., cmd+f15, ctrl+shift+a). Default: {DEFAULT_HOTKEY}')
    parser.add_argument('-dest1', default=None,
                        help='First OSC destination as IP:PORT (e.g., 10.10.20.101:5000)')
    parser.add_argument('-dest2', default=None,
                        help='Second OSC destination as IP:PORT (optional)')
    parser.add_argument('-oscpath', default=DEFAULT_OSC_PATH,
                        help=f'OSC path to send to (e.g., /millumin/action/launchNextColumn). Default: {DEFAULT_OSC_PATH}')
    parser.add_argument('-oscval', default=DEFAULT_OSC_VALUE,
                        help=f'OSC value to send (string). Default: {DEFAULT_OSC_VALUE}')

    return parser.parse_args()


def main():
    """Main entry point"""
    try:
        args = parse_args()
    except SystemExit:
        # argparse calls sys.exit on --help, re-raise to exit cleanly
        raise
    app = OSCSendApp(args)
    app.start()


if __name__ == '__main__':
    main()
