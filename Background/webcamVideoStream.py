from DataStructures.makesmithInitFuncs import MakesmithInitFuncs
import threading
import cv2
import time
import base64


class WebcamVideoStream(MakesmithInitFuncs):
    th = None
    lastCameraRead = 0
    stopped = True
    suspended = False
    stream = None
    height = 640
    width = 480
    fps = 5
    videoSize = "640x480"
    cameraSleep = 0.01
    
    def __init__(self, src=0):
        # initialize the video camera stream and read the first frame
        # from the stream
        #self.stream = cv2.VideoCapture(src)


        #(self.grabbed, self.frame) = self.stream.read()
        # initialize the variable used to indicate if the thread should
        # be stopped
        #self.stopped = True
        #self.suspended = False
        print("Camera initialized")

    def getSettings(self, src=0):
        cameraOff = False
        if self.stream is None:
            self.stream = cv2.VideoCapture(src)
            self.setVideoSize()
            self.setFPS()
            cameraOff = True
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
        self.data.console_queue.put("CAP_PROP_RECTIFICATION=" + str(self.stream.get(cv2.CAP_PROP_RECTIFICATION)))
        self.data.console_queue.put("CAP_PROP_ISO_SPEED=" + str(self.stream.get(cv2.CAP_PROP_ISO_SPEED)))
        self.data.console_queue.put("CAP_PROP_BUFFERSIZE=" + str(self.stream.get(cv2.CAP_PROP_BUFFERSIZE)))
        if cameraOff:
            self.stream.release()
            self.stream = None

    def start(self, src = 0):
        # start the thread to read frames from the video stream
        print("Starting camera thread")
        if self.stream is None:
            self.stream = cv2.VideoCapture(src)
            (self.grabbed, self.frame) = self.stream.read()
            self.setVideoSize()
            self.setFPS()
        #Thread(target=self.update, args=()).start()
        if self.stopped == True:
            self.th = threading.Thread(target=self.update)
            self.th.daemon = True
            self.th.start()
            self.stopped = False
            print("Camera thread started")
            self.data.ui_queue.put("Action:updateCamera_on")
        else:
            print("Camera already started")
        return self

    def update(self):
        # keep looping infinitely until the thread is stopped
        while True:
            time.sleep(self.cameraSleep)
            if not self.data.continuousCamera or time.time()-self.lastCameraRead < 20:
                (self.grabbed, self.frame) = self.stream.read()
                self.suspended = False
            else:
                if self.suspended == False:
                    self.data.ui_queue.put("Action:updateCamera_off")
                self.suspended=True
            # if the thread indicator variable is set, stop the thread
            if self.stopped:
                self.stream.release()
                self.stream = None
                self.data.ui_queue.put("Action:updateCamera_off")
                return
            # otherwise, read the next frame from the stream
            
            small = cv2.resize(self.frame, (256,192))
            imgencode = cv2.imencode(".png",small )[1]
            stringData = base64.b64encode(imgencode).decode()
            self.data.cameraImage = stringData
            self.data.cameraImageUpdated = True
            


    def read(self):
        # return the frame most recently read
        #print("Reading camera frame")
        if self.suspended:
            (self.grabbed, self.frame) = self.stream.read()
            self.suspended = False
            self.data.ui_queue.put("Action:updateCamera_on")
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

    def changeSetting(self, key, value):
        if key == 'fps' and value != self.fps:
            self.fps = value
            if self.stream is not None:
                self.setFPS()
        if key == 'videoSize' and value != self.videoSize:
            self.videoSize = value
            if self.stream is not None:
                self.setVideoSize()
        if key == 'cameraSleep' and value != self.cameraSleep:
            if value<1:
                print("changing sleep interval")
                self.cameraSleep = value
                if self.stream is not None:
                    self.stopped = True
                    self.stream.join()
                    self.start()

    def setFPS(self):
        self.stream.set(cv2.CAP_PROP_FPS, self.fps)

    def setVideoSize(self):
        width = 640
        height = 480
        if self.videoSize == '1024x768':
            width = 1024
            height = 768
        self.stream.set(cv2.CAP_PROP_FRAME_HEIGHT, height)
        self.stream.set(cv2.CAP_PROP_FRAME_WIDTH, width)
