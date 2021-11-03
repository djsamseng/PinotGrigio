import argparse
import asyncio

import audio_managers
import connection_managers
import joystick_managers

async def main():
    args = parse_args()
    video_stream_manager = connection_managers.VideoStreamManager(args.rpi_url)
    joystick_manager = joystick_managers.JoystickManager()
    audio_manager = audio_managers.AudioManager()
    socketio_manager = connection_managers.SocketIOManager(
        joystick_manager=joystick_manager,
        audio_manager=audio_manager,
        register_for_rpi_audio=True
    )
    await socketio_manager.connect_sio()
    while True:
        await socketio_manager.tick(0.001)
        video_stream_manager.tick()


    video_stream_manager.destroy()

def parse_args():
    parser = argparse.ArgumentParser(description="Compute platform")
    parser.add_argument(
        "rpi_url",
        nargs="?",
        const="http://192.168.1.112",
        default="http://192.168.1.112",
        help="Url of the raspberry pi"
    )
    return parser.parse_args()

async def close():
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
            main()
        )
    except KeyboardInterrupt as e:
        print("Keyboard Interrupt")
    finally:
        print("Cleaning up")
        loop.run_until_complete(
            close()
        )

        print("Exiting")
