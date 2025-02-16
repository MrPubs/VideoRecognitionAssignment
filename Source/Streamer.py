import cv2
from multiprocessing import Queue as mp_Queue

class StreamerComponent():
    '''

    Streamer Component, responsible for extracting frames and sending to application
    '''
    def __init__(self, output_queue: mp_Queue):
        '''

        Setup..
        :param output_queue: Queue to push extracted Frames into..
        '''
        # Setup
        self.output_queue = output_queue

    def extractVideo(self, video_path: str) -> None:
        '''

        Main Loop, Extracts from video frame by frame, and puts them on queue to application
        :param video_path:
        :return:
        '''
        # streamline input
        video_to_extract = video_path

        # Open Stream and validate it
        cap = cv2.VideoCapture(video_to_extract)
        fps = cap.get(cv2.CAP_PROP_FPS)
        frame_delay = int(1000/fps)

        if not cap.isOpened():

            print("[STREAMER] Error: Could not open video!")

        # Start Drawing!
        frame_count = 0
        while True:

            # Acquire Frame!
            ret, frame = cap.read()
            frame_count += 1

            # Debug Announce
            # print(f"[STREAMER] Frame #{frame_count} Acquired!")

            # if no more frames stop
            if not ret:
                break

            # push frame back  | TODO: Since required frame by detector is in greyscale format, maybe send greyscale?
            self.output_queue.put(frame)

            # Flow Control..
            # cv2.waitKey(frame_delay)



if __name__ == '__main__':

    # Params
    output_queue = mp_Queue()

    # Component
    streamer = StreamerComponent(output_queue=output_queue)
    streamer.extractVideo(video_path=streamer.defaultVideoPath)

    # Empty Queue
    while not output_queue.empty():

        frame = output_queue.get()
        cv2.imshow("Frame", frame)
        cv2.waitKey(1)