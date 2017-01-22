# pulseaudio-streamer
Detects UPnP media renderers to stream audio to

## About
A small python application that scans the network for UPnP device. It
creates a pulseaudio null sink for each. This allows you select it as an
output devices for each application in puvucontrol. When a sync becomes active
the monitor for it gets encoded and streamed over the network to the UPnP
device.  
  
The functionality of this is a copy of [pulseaudio-dlna][pa dlna]. The reason I
decided to recreate it was because of a number bugs I had experienced when
using pulseaudio-dlna with [gmediarender-reserect][gmr] which I have running on
raspberry pi.  
  
This is a effort to have a seemless experience streaming to gmediarender. At
current it is in very early development and just about works. It is lacking
many features and I cannot say it will support many devices.  
  
The reason I didn't focus my time in trying to improve pulseaudio-dlna was
because I did not know how the UPnP protocol works and thrus decided to build
my own so I could learn. I may at some point go back and debug pulseaudio-dlna
now know how the things work.  
  
## Usage
Clone the repo and run the below in your shell:  
```shell
python2 ./main.py
```
  
If your lucky devices will show in pavucontrol and you will get a dropdown
against each application to select which device you stream to.


[pa dlna]:https://github.com/masmu/pulseaudio-dlna
[gmr]:https://github.com/hzeller/gmrender-resurrect
