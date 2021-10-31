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

## Run

### raspberry pi
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