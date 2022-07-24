# Pinot Grigio

A companion for Pinot

## Installation

Note that socket.io versions need to be compatible. Here we use JS Socket.IO 4.x, python-socketio 5.x, and python-engineio 4.x

### pycli
```bash
$ cd pycli
$ apt-get install python3-pyaudio portaudio19-dev # pyaudio dependencies
$ python -m venv env
$ source ./env/bin/activate
$ pip install -r requirements.txt
```

### raspberry pi
- [Setup instructions](https://www.sigmdel.ca/michel/ha/rpi/streaming_en.html)
```bash
$ sudo apt-get install cmake libjpeg8-dev
$ wget https://github.com/jacksonliam/mjpg-streamer/archive/master.zip
$ unzip master.zip
$ cd mjpeg-streamer-master/mjpg-streamer-experimental
$ make
$ sudo make install
```

```bash
sudo apt-get install python3-pyaudio
cd rpi
pip3 install -r requirements.txt
```

## Run

### raspberry pi
### Easy
```bash
cd rpi
python3 stream_stereo.py
```

### Manual
#### Audio RTP/UDP (faster)
On the receiver PC `ifconfig -a | grep 192` -> 192.168.220
On sender PC `ffmpeg -ac 6 -f alsa -i hw:1,0 -acodec mp2 -ab 32k -ac 1 -f rtp rtp://192.168.1.220:5002`
On receiver PC `ffplay -fflags -nobuffer -probesize 32 rtp://192.168.1.220:5002`
#### Audio TCP (lossless)
On the sender PC `ifconfig -a | grep 192` -> 192.168.1.73
```bash
ffmpeg -ac 6 -f alsa -i hw:1,0 -acodec mp2 -ab 32k -ac 1 -f wav -listen 1 tcp://192.168.1.73:5002
```
#### Webcam
```bash
$ /usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -d /dev/video0 -n -f 10 -r 1280x720" -o "/usr/local/lib/mjpg-streamer/output_http.so -p 8085 -w /usr/local/share/mjpg-streamer/www"
```
- Go to http://192.168.1.73:8085/stream.html
```bash
$ /usr/local/bin/mjpg_streamer -i "/usr/local/lib/mjpg-streamer/input_uvc.so -d /dev/video2 -n -f 10 -r 1280x720" -o "/usr/local/lib/mjpg-streamer/output_http.so -p 8086 -w /usr/local/share/mjpg-streamer/www"
```
- Go to http://192.168.1.73:8086/stream.html
```
$ pkill -9 mjpg_streamer # sometimes needed to fully close and unlock the camera
```

### pycli
```bash
$ python3 main.py # python 3.8.10
$ pkill -9 python3 # sometimes needed to fully close and unlock the camera
```

## ODAS
1. Launch the odas webclient on the PC `$ cd odas_web && npm start`
2. Set odas.cfg on the rpi to have the url of the pc running the webclient
3. Launch odaslive on the rpi `$ cd bin && ./odaslive -c odas.cfg
