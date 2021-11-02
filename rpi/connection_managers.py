

import asyncio
import socketio

class SocketIOManager():
    def __init__(
            self,
            servo_manager=None,
            motor_manager=None):
        self.sio = socketio.AsyncClient()
        self.servo_manager = servo_manager
        self.motor_manager = motor_manager
        self.__hookup_sio()

    async def connect_sio(self, url):
        await self.sio.connect(url)
        room = "foo"
        await self.sio.emit("create or join", room)
        await self.sio.emit("registerForMotorControl")

    async def tick(self, sleep_interval):
        await self.sio.sleep(sleep_interval)

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


