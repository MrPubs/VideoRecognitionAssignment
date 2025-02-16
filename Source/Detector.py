import cv2
import imutils
from multiprocessing import Pipe

class DetectorComponent():
    '''

    Detector component for detecting bounding boxes of people. uses Motion Detection based on Background Subtraction
    '''
    def __init__(self, pipe: Pipe, stopFlag):
        '''

        Setup..
        :param pipe: Pipe for communication
        :param stopFlag: Flag to signal end of video
        '''
        # Setup
        self.pipe = pipe
        self.prev_frame = None
        self.current_frame = None

        # State
        self.stopFlag = stopFlag

    @staticmethod
    def getCountours(frame, prev_frame) -> None:
        '''

        Gets the contours of the people (moving objects)
        :param frame: frame to analyse
        :param prev_frame: frame to use as a reference
        :return: None!
        '''
        # Given Code..
        diff = cv2.absdiff(frame, prev_frame)
        thresh = cv2.threshold(diff, 25, 255, cv2.THRESH_BINARY)[1]
        thresh = cv2.dilate(thresh, None, iterations=2)
        cnts = cv2.findContours(thresh.copy(), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        cnts = imutils.grab_contours(cnts)

        return cnts

    def work(self) -> None:
        '''

        Main Loop, Get from application frames drawn from streamer, analyze, and return the results back to application
        for viewport component to utilize.
        :return: None!
        '''
        while not self.stopFlag.is_set():

            # Check if has frame
            if self.pipe.poll():

                # Get Frame from App
                frame = self.pipe.recv()
                gs_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

                # Check if prev already populated
                if self.prev_frame is None:
                    self.prev_frame = gs_frame
                    continue

                # TODO: For some reason, despite same frame, contours are different than added code;
                #   requires debugging but skipped because instruction says to not pay attention to quality of detection.
                # find Contours and send back
                self.current_frame = gs_frame
                cnts = self.getCountours(self.current_frame, self.prev_frame)
                self.pipe.send((frame, cnts))


if __name__ == '__main__':

    detector = DetectorComponent()
    detector.work()