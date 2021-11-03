import argparse
import asyncio
from multiprocessing import Process
import subprocess

import audio_managers
import connection_managers
import robot_managers

SERVER_URL = "http://192.168.1.220:4000"

def launch_mjpg_streamer(device_name, port):
    mjpg_streamer_path = "/usr/local/lib/mjpg-streamer"
    subprocess.run(
        '/usr/local/bin/mjpg_streamer ' + \
        '-i "/usr/local/lib/mjpg-streamer/input_uvc.so -d ' + device_name + ' -n -f 10 -r 1280x720" ' + \
        '-o "/usr/local/lib/mjpg-streamer/output_http.so -p ' + port + ' -w /usr/local/share/mjpg-streamer/www" ',
        shell=True, check=True)

def parse_args():
    parser = argparse.ArgumentParser(description="Raspberry Pi Controller")
    parser.add_argument(
            "vd1",
            nargs="?",
            const="/dev/video0",
            default="/dev/video0",
            help="Video device 1 (ex: /dev/video0)")
    parser.add_argument(
            "vd2",
            nargs="?",
            const="/dev/video2",
            default="/dev/video2",
            help="Video device 2 (ex: /dev/video2)")
    return parser.parse_args()

async def main():
    args = parse_args()
    p1 = Process(target=launch_mjpg_streamer, args=(args.vd1, "8085"))
    p2 = Process(target=launch_mjpg_streamer, args=(args.vd2, "8086"))
    p1.start()
    p2.start()

    servo_manager = robot_managers.ServoManager()
    motor_manager = robot_managers.MotorManager()
    audio_manager = audio_managers.AudioManager()
    socketio_manager = connection_managers.SocketIOManager(
            servo_manager=servo_manager,
            motor_manager=motor_manager,
            audio_manager=audio_manager,
    )
    await socketio_manager.connect_sio(SERVER_URL)
    while True:
        await socketio_manager.tick(0.001)
    p1.join()
    p2.join()

async def close():
    await asyncio.sleep(0.1)

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    try:
        loop.run_until_complete(
                main()
        )
    except KeyboardInterrupt as e:
        print("Keyboard interrupt")
    finally:
        print("Cleaning up")
        loop.run_until_complete(
                close()
        )
        print("Exiting")
