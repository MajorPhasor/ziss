# ISS Tracker and APRS Location Beacon

import serial
import math
import time
from datetime import datetime
import ephem
import subprocess
from pydub import AudioSegment

mycall = 'MYCALL'
 
degrees_per_radian = 180.0 / math.pi

gps = serial.Serial('/dev/ttyUSB0', 4800)

needData = 1;

def getGPSfix():
    gpsString = ''
    while -1 == gpsString.find('$GPGGA'):
        gpsString = gps.readline()
    latitudeDegrees = gpsString[18:20]
    latitudeMinutes = gpsString[20:27]
    latitudeMinutes = str(float(latitudeMinutes) / 60)
    latitudeDecimal = latitudeMinutes.find('.')
    latitude = latitudeDegrees + latitudeMinutes[latitudeDecimal:len(latitudeMinutes)]
    global APRSlat
    APRSlat = gpsString[18:25]
    global NS
    NS = gpsString[28:29]
    longitudeDegrees = gpsString[30:33]
    longitudeMinutes = gpsString[33:40]
    longitudeMinutes = str(float(longitudeMinutes) / 60)
    longitudeDecimal = longitudeMinutes.find('.')
    longitude = longitudeDegrees + longitudeMinutes[longitudeDecimal:len(longitudeMinutes)]
    global APRSlong
    APRSlong = gpsString[30:38]
    global EW
    EW = gpsString[41:42]
    global globalLat
    globalLat = float(latitude)
    if NS == 'S':
        globalLat = -1 * globalLat
    global globalLong
    globalLong = float(longitude)
    if EW == 'W':
        globalLong = -1 * globalLong
    
# need python-pyserial and python-pyaudio and python-setuptools and python-dev

def issPos(): # Subroutine code source based on: http://www.sharebrained.com/2011/10/18/track-the-iss-pyephem/
    home = ephem.Observer()
    global globalLat
    global globalLong
    home.lat = str(globalLat)   # +N
    home.lon = str(globalLong)  # +E
    home.elevation = 80 # meters
 
    # Always get the latest ISS TLE data from:
    # http://spaceflight.nasa.gov/realdata/sightings/SSapplications/Post/JavaSSOP/orbit/ISS/SVPOST.html
    iss = ephem.readtle('ISS',
        '1 25544U 98067A   17121.54079120  .00016717  00000-0  10270-3 0  9007',
        '2 25544  51.6391 270.8069 0005706 116.0974 244.0766 15.53922524 14490'
    )
    home.date = datetime.utcnow()
    iss.compute(home)
    global issElevation
    global issAzimuth
    issElevation = "{:4.1f}".format(iss.alt*degrees_per_radian)
    issAzimuth =  "{:5.1f}".format(iss.az*degrees_per_radian)
    
attempt = 0
while attempt <= 100:
    getGPSfix()
    print('Current location is: %4.2f by %5.2f') % (globalLat, globalLong)
    aprsString = mycall + ">CQ,RS0ISS:=" + APRSlat + NS + "/" + APRSlong + EW + "-Greets from RPI"
    print(aprsString)
    issPos()
    print('Current ISS elevation is: ' + issElevation + 'degrees and azimuth is: ' + issAzimuth)
    if float(issElevation) > 0:
        print('The ISS is in view!')
    else:
        print('The ISS is not in view.')
    with open("aprsString.txt", "w") as aprsOutputFile:
        aprsOutputFile.write(aprsString)
    subprocess.call(["gen_packets","-o", "aprsOutput.wav", "-a", "150", "aprsString.txt"])
    dataAudio = AudioSegment.from_wav("aprsOutput.wav")
    zerosAudio = AudioSegment.from_wav("aprszero.wav")
    txaudio = zerosAudio + dataAudio
    txaudio.export("txaudio.wav", format="wav")
    subprocess.call(["play", "txaudio.wav"])
    attempt = attempt + 1
    time.sleep(30)

