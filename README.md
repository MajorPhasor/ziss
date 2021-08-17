# ziss
Ziss takes input from a USB GPS receiver and TLE data for the ISS to predict passes and generates an APRS packet with your location to send to the amateur radio repeater.

I never got it to work with the ISS with a 5W handheld transciever, but was able to set the frequency for a local APRS digipeater and see my location plotted on aprs.fi

The code was written for Python 2.7, with the goal of running it on a Raspberry Pi. I think I used a Behringer USB Audio device for the output.

I ended up making my own vox circuit to trigger transmit on my Yaesu VX-6 when there was an audio output.

Hopefully you'll find some of this code useful!
