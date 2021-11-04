from multiprocessing import Process, Queue
import pyaudio

RESPEAKER_RATE = 16000
RESPEAKER_CHANNELS = 6
RESPEAKER_WIDTH = 2
CHUNK = 1024

class AudioRecorderP2():
    def __init__(self):
        self.p = pyaudio.PyAudio()

    def open_stream(self):
        respeaker_index = self.__find_respeaker_index()
        if respeaker_index is None:
            return False

        self.stream = self.p.open(
            rate=RESPEAKER_RATE,
            format=self.p.get_format_from_width(RESPEAKER_WIDTH),
            channels=RESPEAKER_CHANNELS,
            input=True,
            output=True,
        )
        return True
    
    def __find_respeaker_index(self):
        info = self.p.get_host_api_info_by_index(0)
        num_devices = info.get('deviceCount')
        for i in range(0, num_devices):
            device_data = self.p.get_device_info_by_host_api_device_index(0, i)
            device_name = device_data.get('name')
            print("Device:", device_name, "Idx:", i, "Max channels:", device_data.get('maxInputChannels'))
            if device_name.startswith("ReSpeaker 4 Mic Array (UAC1.0): USB Audio"):
                return i

        return None

    def tick(self, play_data=None):
        data = self.stream.read(CHUNK)
        if play_data is not None:
            self.stream.write(play_data, CHUNK)
        return data

def test_audio_recorder():
    audio_recorder = AudioRecorderP2()
    audio_recorder.open_stream()
    while True:
        data = audio_recorder.tick()

def record_p2(queue, play_queue):
    audio_recorder = AudioRecorderP2()
    did_open = audio_recorder.open_stream()
    if not did_open:
        print("ReSpeaker not found. Not recording audio")
        return

    while True:
        play_data = None
        if not play_queue.empty():
            play_data = play_queue.get()
        data = audio_recorder.tick(play_data)
        queue.put(data)

class AudioManager():
    def __init__(self):
        self.queue = Queue()
        self.play_queue = Queue()
        self.process = Process(target=record_p2, args=(self.queue, self.play_queue))
        self.process.start()

    
    def tick(self):
        frames = []
        while not self.queue.empty():
            data = self.queue.get()
            if data is not None:
                frames.append(data)
        return frames

    def put_play_data(self, play_data):
        for chunk in play_data:
            self.play_queue.put(chunk)


if __name__ == "__main__":
    test_audio_recorder()
