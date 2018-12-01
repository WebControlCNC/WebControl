from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import threading
import cv2
import time
import base64


class WebcamVideoStream(MakesmithInitFuncs):
    th = None
    
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)
        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = False
        print("Camera initialized")

    def start(self):
        # start the thread to read frames from the video stream
        print("Starting camera thread")
        #Thread(target=self.update, args=()).start()
        if self.stopped == True:
            self.th = threading.Thread(target=self.update)
            self.th.daemon = True
            self.th.start()
            self.stopped = False
            print("Camera thread started")
        else:
            print("Camera alrady started")
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            time.sleep(0.001)
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            (self.grabbed, self.frame) = self.stream.read()
            '''small = cv2.resize(self.frame, (256,192))
            imgencode = cv2.imencode(".png",small )[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.cameraImage = stringData
            self.data.cameraImageUpdated = True
            '''


    def read(self):
        # return the frame most recently read
        #print("Reading camera frame")
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        print("Stopping camera")
        self.stopped = True
