"""
Setup script for creating macOS .app bundle
Usage: python setup.py py2app
"""

from setuptools import setup

APP = ['src/oscusend.py']
DATA_FILES = []
OPTIONS = {
    'argv_emulation': False,
    'iconfile': None,
    'plist': {
        'CFBundleName': 'OSCUsend',
        'CFBundleDisplayName': 'OSCUsend',
        'CFBundleGetInfoString': 'Global hotkey to OSC message converter',
        'CFBundleIdentifier': 'com.oscusend.app',
        'CFBundleVersion': '1.0.0',
        'CFBundleShortVersionString': '1.0.0',
        'NSAppleScriptEnabled': False,
        'LSBackgroundOnly': True,
    },
    'packages': ['pynput', 'pythonosc'],
}

setup(
    name='OSCUsend',
    app=APP,
    data_files=DATA_FILES,
    options={'py2app': OPTIONS},
    setup_requires=['py2app'],
    install_requires=[
        'pynput>=1.7.6',
        'python-osc>=1.8.0',
    ],
)
