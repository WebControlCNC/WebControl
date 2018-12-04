from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import threading
import cv2
import time
import base64


class WebcamVideoStream(MakesmithInitFuncs):
    th = None
    lastCameraRead = 0
    
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        self.stream = cv2.VideoCapture(src)


        (self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        self.stopped = True
        self.suspended = False
        print("Camera initialized")

    def getSettings(self):
        self.data.console_queue.put("CAP_PROP_POS_MSEC=" + str(self.stream.get(cv2.CAP_PROP_POS_MSEC)))
        self.data.console_queue.put("CAP_PROP_POS_FRAMES=" + str(self.stream.get(cv2.CAP_PROP_POS_FRAMES)))
        self.data.console_queue.put("CAP_PROP_POS_AVI_RATIO=" + str(self.stream.get(cv2.CAP_PROP_POS_AVI_RATIO)))
        self.data.console_queue.put("CAP_PROP_FRAME_WIDTH=" + str(self.stream.get(cv2.CAP_PROP_FRAME_WIDTH)))
        self.data.console_queue.put("CAP_PROP_FRAME_HEIGHT=" + str(self.stream.get(cv2.CAP_PROP_FRAME_HEIGHT)))
        self.data.console_queue.put("CAP_PROP_FPS=" + str(self.stream.get(cv2.CAP_PROP_FPS)))
        self.data.console_queue.put("CAP_PROP_FOURCC=" + str(self.stream.get(cv2.CAP_PROP_FOURCC)))
        self.data.console_queue.put("CAP_PROP_FRAME_COUNT=" + str(self.stream.get(cv2.CAP_PROP_FRAME_COUNT)))
        self.data.console_queue.put("CAP_PROP_FORMAT=" + str(self.stream.get(cv2.CAP_PROP_FORMAT)))
        self.data.console_queue.put("CAP_PROP_MODE=" + str(self.stream.get(cv2.CAP_PROP_MODE)))
        self.data.console_queue.put("CAP_PROP_BRIGHTNESS=" + str(self.stream.get(cv2.CAP_PROP_BRIGHTNESS)))
        self.data.console_queue.put("CAP_PROP_CONTRAST=" + str(self.stream.get(cv2.CAP_PROP_CONTRAST)))
        self.data.console_queue.put("CAP_PROP_SATURATION=" + str(self.stream.get(cv2.CAP_PROP_SATURATION)))
        self.data.console_queue.put("CAP_PROP_HUE=" + str(self.stream.get(cv2.CAP_PROP_HUE)))
        self.data.console_queue.put("CAP_PROP_GAIN=" + str(self.stream.get(cv2.CAP_PROP_GAIN)))
        self.data.console_queue.put("CAP_PROP_EXPOSURE=" + str(self.stream.get(cv2.CAP_PROP_EXPOSURE)))
        self.data.console_queue.put("CAP_PROP_CONVERT_RGB=" + str(self.stream.get(cv2.CAP_PROP_CONVERT_RGB)))
#        self.data.console_queue.put("CAP_PROP_WHITE_BALANCE_U=" + str(self.stream.get(cv2.CAP_PROP_WHITE_BALANCE_U)))
#        self.data.console_queue.put("CAP_PROP_WHITE_BALANCE_V=" + str(self.stream.get(cv2.CAP_PROP_WHITE_BALANCE_V)))
        self.data.console_queue.put("CAP_PROP_RECTIFICATION=" + str(self.stream.get(cv2.CAP_PROP_RECTIFICATION)))
        self.data.console_queue.put("CAP_PROP_ISO_SPEED=" + str(self.stream.get(cv2.CAP_PROP_ISO_SPEED)))
        self.data.console_queue.put("CAP_PROP_BUFFERSIZE=" + str(self.stream.get(cv2.CAP_PROP_BUFFERSIZE)))

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
            time.sleep(0.01)
            if not self.data.continuousCamera or time.time()-self.lastCameraRead < 20:
                (self.grabbed, self.frame) = self.stream.read()
                self.suspended=False
            else:
                self.suspended=True
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                return
            # otherwise, read the next frame from the stream
            
            '''small = cv2.resize(self.frame, (256,192))
            imgencode = cv2.imencode(".png",small )[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.cameraImage = stringData
            self.data.cameraImageUpdated = True
            '''


    def read(self):
        # return the frame most recently read
        #print("Reading camera frame")
        if self.suspended:
            (self.grabbed, self.frame) = self.stream.read()
            self.suspended = False
        self.lastCameraRead = time.time()
        
        if self.stopped:
            self.start()
        return self.frame

    def stop(self):
        # indicate that the thread should be stopped
        print("Stopping camera")
        self.stopped = True

    def status(self):
        if self.stopped:
            return("stopped")
        if self.suspended:
            return("suspended")
        return("running")