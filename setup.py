#! /usr/bin/python2

from setuptools import setup, find_packages
from codecs import open

with open('./README.rst', 'r', 'utf-8') as f:
    long_description = f.read()

setup(
    name='pulseaudio-streamer',
    description='Detects UPnP media renderers to stream audio to',
    long_description=long_description,
    version='1.0.0',
    author='Sam Light',
    author_email='info@lightscale.co.uk',
    url='https://github.com/lightscaletech/pulseaudio-streamer',
    platforms='Linux',
    keywords=['pulseaudio', 'upnp', 'dlna', 'streaming', 'audio'],
    packages=find_packages(),
    install_requires=[
        'xmltodict >= 0.10.2'
    ],
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 2.7',
        'Licence :: OSI Approved :: GPLv3',
        'Environment :: Console',
        'Topic :: Multimedia :: Sound/Audio'],
    entry_points={
        'console_scripts':[
            'pulseaudio-streamer=pulseaudio_streamer.main']},
    package_data={
        'pulseaudio_streamer':'upnp/*.xml'
    })
