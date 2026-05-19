#!/usr/bin/env python3
"""
OSCSend - Global hotkey to OSC message converter for macOS
"""

import os
import sys
import logging
import time
from dataclasses import dataclass

from pynput import keyboard
from pythonosc import udp_client
from dotenv import load_dotenv

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

    def __init__(self):
        self.osc_clients = []  # List of (client, destination) tuples
        self.last_trigger_time = 0
        self.trigger_cooldown = 0.2  # Prevent duplicate triggers (seconds)
        self.hotkey_listener = None

        load_dotenv()
        self.config = self._load_config()
        self._setup_osc_clients()

    def _load_config(self) -> dict:
        """Load configuration from environment variables"""
        config = {}

        # Parse hotkey: format should be "cmd+f15" or "cmd+shift+f1"
        hotkey_str = os.getenv('HOTKEY', 'cmd+f15').lower()
        config['hotkey'] = self._parse_hotkey(hotkey_str)

        # OSC Destination 1
        config['dest1'] = OSCDestination(
            ip=os.getenv('OSC_DEST1_IP', '127.0.0.1'),
            port=int(os.getenv('OSC_DEST1_PORT', '8000')),
            path=os.getenv('OSC_DEST1_PATH', '/trigger'),
            value=os.getenv('OSC_DEST1_VALUE', 'activate')
        )

        # OSC Destination 2
        config['dest2'] = OSCDestination(
            ip=os.getenv('OSC_DEST2_IP', '127.0.0.1'),
            port=int(os.getenv('OSC_DEST2_PORT', '8001')),
            path=os.getenv('OSC_DEST2_PATH', '/trigger'),
            value=os.getenv('OSC_DEST2_VALUE', 'activate')
        )

        return config

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
        for dest in [self.config['dest1'], self.config['dest2']]:
            client = udp_client.SimpleUDPClient(dest.ip, dest.port)
            self.osc_clients.append((client, dest))
            logger.info(f"OSC destination configured: {dest.ip}:{dest.port}{dest.path}")

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
                logger.info(f"OSC sent: {dest.ip}:{dest.port}{dest.path} = '{dest.value}'")
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


def main():
    """Main entry point"""
    app = OSCSendApp()
    app.start()


if __name__ == '__main__':
    main()
