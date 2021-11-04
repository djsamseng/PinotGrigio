

import asyncio
import socketio

class SocketIOManager():
    def __init__(
            self,
            servo_manager=None,
            motor_manager=None,
            audio_manager=None):
        self.sio = socketio.AsyncClient()
        self.servo_manager = servo_manager
        self.motor_manager = motor_manager
        self.audio_manager = audio_manager
        self.__hookup_sio()

    async def connect_sio(self, url):
        await self.sio.connect(url)
        room = "foo"
        await self.sio.emit("create or join", room)
        await self.sio.emit("registerForMotorControl")
        await self.sio.emit("registerForPlayAudio")

    async def tick(self, sleep_interval):
        await self.sio.sleep(sleep_interval)
        await self.__audio_tick()

    def __hookup_sio(self):
        sio = self.sio
        @sio.on("motor")
        async def on_motor(data):
            print("Received on_motor:", data)
            if self.servo_manager is not None:
                self.servo_manager.look_right(data["pan_right"])
                self.servo_manager.look_down(data["pan_down"])
            if self.motor_manager is not None:
                self.motor_manager.set_motors(data["left"], data["right"])

        @sio.on("playaudio")
        async def on_playaudio(data):
            if self.audio_manager is not None:
                self.audio_manager.put_play_data(data)

    async def __audio_tick(self):
        if self.audio_manager is None:
            return

        audio_data = self.audio_manager.tick()
        if len(audio_data) > 0:
            await self.sio.emit("rpiaudio", audio_data)


