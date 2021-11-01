

import asyncio
import socketio

class SocketIOManager():
    def __init__(self):
        self.sio = socketio.AsyncClient()
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
