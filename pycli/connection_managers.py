import asyncio
import socketio

import base64
import cv2
import numpy as np
import os
import pyaudio
from scipy.io import wavfile
import urllib.request, urllib.error

class VideoStreamManager():
    def __init__(self, rpi_url) -> None:
        self.rpi_url = rpi_url
        self.cap_left = None
        self.cap_right = None
        self.__try_connect()
        # TODO https://albertarmea.com/post/opencv-stereo-camera/#calibrating-the-cameras
        self.stereo = cv2.StereoBM_create()

    def destroy(self):
        if self.cap_left is not None:
            self.cap_left.release()
        if self.cap_right is not None:
            self.cap_right.release()

    def tick(self):
        if self.cap_left is None or self.cap_right is None:
            self.__try_connect()
            return

        [left_frame, right_frame] = self.__grab_video_stream_parallel([self.cap_left, self.cap_right])
        #left_frame = self.__grab_video_stream(self.cap_left)
        #right_frame = self.__grab_video_stream(self.cap_right)
        if left_frame is None or right_frame is None:
            self.__try_connect()
            return

        cv2.imshow("Left", left_frame)
        cv2.imshow("Right", right_frame)
        if left_frame is not None and right_frame is not None:
            gray_left = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)
            disparity = self.stereo.compute(gray_left, gray_right)
            cv2.imshow("Disparity", disparity / 2048)
            cv2.waitKey(5)

    def __try_connect(self):
        cap_left_url = self.rpi_url + ":8086/?action=stream"
        cap_right_url = self.rpi_url + ":8085/?action=stream"
        try:
            res = urllib.request.urlopen(cap_left_url)
        except urllib.error.URLError:
            return
        if res.getcode() != 200:
            return
        self.cap_left = cv2.VideoCapture(cap_left_url)
        self.cap_right = cv2.VideoCapture(cap_right_url)

    def __grab_video_stream(self, cap):
        # 720, 1280, 3
        ret, frame = cap.read()
        return frame

    def __grab_video_stream_parallel(self, caps):
        for cap in caps:
            cap.grab()
        frames = []
        for cap in caps:
            ret, frame = cap.retrieve()
            frames.append(frame)
        return frames


class SocketIOManager():
    def __init__(
        self,
        joystick_manager=None,
        audio_manager=None,
        register_for_rpi_audio=False,
        register_for_audio_data=False,
        register_for_brain_control=False
    ) -> None:
        self.sio = socketio.AsyncClient()
        self.joystick_manager = joystick_manager
        self.audio_manager = audio_manager
        self.register_for_rpi_audio = register_for_rpi_audio
        self.register_for_audio_data = register_for_audio_data
        self.register_for_brain_control = register_for_brain_control
        self.__hookup_sio()

    async def connect_sio(self):
        await self.sio.connect("http://localhost:4000")
        room = "foo"
        await self.sio.emit("create or join", room)
        if self.register_for_rpi_audio:
            await self.sio.emit("registerForRpiAudio")
        if self.register_for_audio_data:
            await self.sio.emit("registerForAudioData")
        if self.register_for_brain_control:
            await self.sio.emit("registerForBrainControl")

    async def tick(self, sleep_interval):
        await self.sio.sleep(sleep_interval)
        joystick_data = self.joystick_manager.tick()
        if joystick_data is not None:
            print("Emit motor:", joystick_data)
            await self.sio.emit("motor", joystick_data)
        await self.__audio_tick()

    def __hookup_sio(self):
        sio = self.sio

        @sio.on("braincontrol")
        async def on_brain_control(data):
            # Comes from web browser
            print("BRAIN:", data)
            if "speak" in data:
                print("SPEAK:", data["speak"])
                text = data["speak"].lower()
                filename = "./wav/" + text + ".wav"
                if os.path.exists(filename):
                    self.webrtc_manager.audio_replay_track.openWave(filename)
                else:
                    print("Cannot speak: no file")

        @sio.on("rpiaudio")
        async def on_rpi_audio(data):
            if self.audio_manager is not None:
                self.audio_manager.put_play_data(data)


        @sio.on("audiodata")
        async def on_audio_data(data):
            try:
                vals = data.split(",")
                vals = np.array([int(v) for v in vals if v])
                '''
                if do_graph:
                    if itr + len(vals) >= to_graph.shape[0]:
                        itr = 0
                    to_graph[itr:itr + len(vals)] = vals[:]
                    itr += len(vals)
                    line.set_ydata(to_graph)
                    fig.canvas.draw()
                    fig.canvas.flush_events()
                '''
            except Exception as e:
                print(e)

        @sio.on("frame")
        async def on_frame(data):
            data = base64.b64decode(data)
            data = np.frombuffer(data, dtype=np.uint8)
            data = cv2.imdecode(data, flags=cv2.IMREAD_COLOR)
            cv2.imshow("frame", data)
            cv2.waitKey(5)

    async def __audio_tick(self):
        record_data = self.audio_manager.tick()
        if len(record_data) > 0:
            await self.sio.emit("playaudio", record_data)