from multiprocessing import Process
import subprocess


def launch_mjpg_streamer(device_name, port):
    mjpg_streamer_path = "/usr/local/lib/mjpg-streamer"
    subprocess.run(
        '/usr/local/bin/mjpg_streamer ' + \
        '-i "/usr/local/lib/mjpg-streamer/input_uvc.so -d ' + device_name + ' -n -f 10 -r 1280x720" ' + \
        '-o "/usr/local/lib/mjpg-streamer/output_http.so -p ' + port + ' -w /usr/local/share/mjpg-streamer/www" ',
        shell=True, check=True)

def main():
    p1 = Process(target=launch_mjpg_streamer, args=("/dev/video1", "8085"))
    p2 = Process(target=launch_mjpg_streamer, args=("/dev/video3", "8086"))
    p1.start()
    p2.start()
    p1.join()
    p2.join()

if __name__ == "__main__":
    main()
