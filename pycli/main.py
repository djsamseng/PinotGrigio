import cv2

RPI_URL = "http://192.168.1.80"
RPI_LEFT_CAMERA = RPI_URL + ":8086/?action=stream"
RPI_RIGHT_CAMERA = RPI_URL + ":8085/?action=stream"

def grab_video_stream(cap, name):
    ret, frame = cap.read()
    cv2.imshow(name, frame)
    cv2.waitKey(5)
    return frame

def main():
    cap_left = cv2.VideoCapture(RPI_LEFT_CAMERA)
    cap_right = cv2.VideoCapture(RPI_RIGHT_CAMERA)
    # TODO https://albertarmea.com/post/opencv-stereo-camera/#calibrating-the-cameras
    stereo = cv2.StereoBM_create()
    while True:
        left_frame = grab_video_stream(cap_left, "Left")
        right_frame = grab_video_stream(cap_right, "Right")
        if left_frame is not None and right_frame is not None:
            gray_left = cv2.cvtColor(left_frame, cv2.COLOR_BGR2GRAY)
            gray_right = cv2.cvtColor(right_frame, cv2.COLOR_BGR2GRAY)
            disparity = stereo.compute(gray_left, gray_right)
            cv2.imshow("Disparity", disparity / 2048)
            cv2.waitKey(5)
        else:
            print("No Frame!")


    cap1.release()
    cap2.release()

if __name__ == "__main__":
    main()