from setuptools import setup
from codecs import open

with open('./README.rst', 'utf-8') as f:
    long_description = f.read()

setup(
    name='pulseaudio-streamer',
    description='Detects UPnP media renderers to stream audio to',
    long_description=long_description,
    version='1.0.0')
