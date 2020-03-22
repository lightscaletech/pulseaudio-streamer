pulseaudio-streamer
===================

Detects UPnP media renderers to stream audio to

About
-----

A small Python application that scans the network for UPnP devices. It
creates a pulseaudio null sink for each. This allows you select it as
output devices for each application in pavucontrol. When a sink becomes
active the monitor for it gets encoded and streamed over the network to
the UPnP device.

The functionality of this is a copy of `pulseaudio-dlna`_. The reason I
decided to recreate it was because of a number bugs I had experienced
when using pulseaudio-dlna with `gmediarender-resurrect`_ which I have
running on Raspberry Pi.

This is an effort to have a seamless experience streaming to
gmediarender. At current it is in very early development and just about
works. It is lacking many features and I cannot say it will support many
devices.

The reason I didn’t focus my time in trying to improve pulseaudio-dlna
was because I did not know how the UPnP protocol works and thus decided
to build my own so I could learn. I may at some point go back and debug
pulseaudio-dlna now that I know how the things work.

Usage
-----

Clone the repo and run the commands below in your shell:

.. code:: shell
    
    cd pulseaudio-streamer
    python -m pulseaudio_streamer

If you are lucky devices will show in pavucontrol and you will get a
dropdown against each application to select which device you stream to.
 
Install
-----

Clone the repo and cd into it. Then run the following:

.. code:: shell

    python setup.py install
    
You will require root access to install this so use :code:`sudo` if you are not logged in as root.

Once the application is installed you will be able to run it from the shell by using :code:`pulseaudio-streamer`.
 

Copyright (c) 2017 Lightscale Tech Ltd

.. _pulseaudio-dlna: https://github.com/masmu/pulseaudio-dlna
.. _gmediarender-reserect: https://github.com/hzeller/gmrender-resurrect
