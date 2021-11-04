from multiprocessing import Process, Queue
import numpy as np
import pyaudio
import time

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
CHUNK = 1024

class AudioPlayer():
    def __init__(self) -> None:
        self.p = pyaudio.PyAudio()
        self.__find_respeaker_index()

    def open_stream(self):
        self.stream = self.p.open(
            rate=RESPEAKER_RATE,
            format=self.p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            output=True,
        )

    def __find_respeaker_index(self):
        num_hosts = self.p.get_host_api_count()
        for host_idx in range(num_hosts):
            info = self.p.get_host_api_info_by_index(host_idx)
            num_devices = info.get('deviceCount')
            for i in range(0, num_devices):
                device_data = self.p.get_device_info_by_host_api_device_index(host_idx, i)
                device_name = device_data.get('name')
                maxChannels = device_data.get("maxInputChannels")
                print("Device:", device_name, "host_idx", host_idx, "device_idx:", i, "Max channels:", maxChannels)

    def tick(self, play_chunk=None):
        data = self.stream.read(CHUNK)
        if play_chunk is not None:
            self.stream.write(play_chunk, CHUNK)
        return data
        

def test_audio_player():
    audio_player = AudioPlayer()
    audio_player.open_stream()

def play_p2(play_queue, record_queue):
    audio_player = AudioPlayer()
    audio_player.open_stream()
    while True:
        time.sleep(0.0001)
        data = None
        if not play_queue.empty():
            data = play_queue.get()
        record_data = audio_player.tick(data)
        record_queue.put(record_data)

class AudioManager():
    def __init__(self) -> None:
        self.queue = Queue()
        self.record_queue = Queue()
        self.process = Process(target=play_p2, args=(self.queue, self.record_queue))
        self.process.start()

    def tick(self):
        frames = []
        while not self.record_queue.empty():
            data = self.record_queue.get()
            if data is not None:
                frames.append(data)
        return frames

    def put_play_data(self, play_data):
        for chunk in play_data:
            self.queue.put(chunk)

if __name__ == "__main__":
    test_audio_player()