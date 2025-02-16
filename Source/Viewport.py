
import cv2
import multiprocessing as mp

class ViewportComponent():
    '''

    Display Frames after applying Post-Processing Pass
    '''
    def __init__(self, input_queue: mp.Queue, stopFlag: mp.Event):
        '''

        Setup..
        :param input_queue: Queue to take frames and contours from
        :param stopFlag: Flag to signal end of video
        '''
        # Setup
        self.input_queue = input_queue

        # Counter
        self.frame_counter = 0

        # State
        self.stopFlag = stopFlag

    @staticmethod
    def applyContours(frame, contours, blur=False) -> None:
        '''

        :param frame: frame to apply contour to (and optionaly blur)
        :param contours: contours to apply to frame
        :param blur:  wether to apply blur or not
        :return: None!
        '''

        for contour in contours:
            if cv2.contourArea(contour) > 500:  # Filter out small contours
                (x, y, w, h) = cv2.boundingRect(contour)
                cv2.rectangle(frame, (x, y), (x + w, y + h), (0, 255, 0), 2)

                # Conditional blur
                if blur:

                    roi = frame[y:y + h, x:x + w]  # Extract the region of interest
                    blurred_roi = cv2.GaussianBlur(roi, (15, 15), 0)  # Apply Gaussian Blur
                    frame[y:y + h, x:x + w] = blurred_roi  # Replace with blurred version

    def work(self) -> None:
        '''

        component main work loop, get frame, apply Post-Process pass, and show!
        :return: None!
        '''
        # Work loop
        while not self.stopFlag.is_set():

            # if has new data
            if not self.input_queue.empty():

                # Count
                self.frame_counter += 1

                # Get Frame apply contours, blur and show!
                frame, contours = self.input_queue.get()
                self.applyContours(frame=frame, contours=contours, blur=True)
                cv2.imshow("Viewport", frame)
                cv2.waitKey(1)


if __name__ == '__main__':

    queue = mp_Queue()

    viewport = ViewportComponent(input_queue=queue)
    viewport.work()