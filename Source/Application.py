import yaml
import multiprocessing as mp
from time import time

# Components source
from Source.Detector import DetectorComponent
from Source.Viewport import ViewportComponent
from Source.Streamer import StreamerComponent

class Application():
    '''

    Orchestrates all the components to work together in synchronization
    '''

    def __init__(self, config_path: str):

        # Config management
        self.config_path = config_path
        with open(self.config_path) as stream:
            self.config_contents = yaml.safe_load(stream=stream)

        # State
        self.stopFlag = mp.Event() # Stop Session flag!

        # Component Management:
        # - Streamer
        self.streamer_outputs = mp.Queue() # Queue for fifo
        self.streamer_proc = mp.Process(target=self.operateStreamer,
                                        args=(self.streamer_outputs, self.config_contents['streamer']['video_path']))

        # - Detector
        self.detector_pipe_parent_conn, self.detector_pipe_child_conn = mp.Pipe() # Pipe for bidirectional Communication
        self.detector_proc = mp.Process(target=self.operateDetector, args=(self.detector_pipe_child_conn, self.stopFlag))

        # - Viewport
        self.viewport_inputs = mp.Queue() # Queue for fifo
        self.viewport_proc = mp.Process(target=self.operateViewport, args=(self.viewport_inputs, self.stopFlag))

        # Counter
        self.frame_counter = 0

    @staticmethod
    def operateStreamer(output_queue: mp.Queue, video_path: str):
        streamer = StreamerComponent(output_queue=output_queue)
        streamer.extractVideo(video_path=video_path)

    @staticmethod
    def operateViewport(input_queue: mp.Queue, stopFlag: mp.Event):
        viewport = ViewportComponent(input_queue=input_queue, stopFlag=stopFlag)
        viewport.work()

    @staticmethod
    def operateDetector(pipe: mp.Pipe, stopFlag: mp.Event):
        detector = DetectorComponent(pipe=pipe, stopFlag=stopFlag)
        detector.work()

    def work(self) -> None:
        '''

        Start the application, component by component, run them and enter the main loop
        :return: None!
        '''
        # Start Proccesses
        self.streamer_proc.start()
        self.detector_proc.start()
        self.viewport_proc.start()

        # Main Loop!
        video_playing = False
        timestamp = time()
        while True:

            # if has frame, send to viewport
            if not self.streamer_outputs.empty():

                # Time analysis
                timestamp_memory = timestamp
                timestamp = time()
                timedelta = timestamp - timestamp_memory
                fps = int(1/timedelta)
                print(f"FPS: {fps}")

                # Flag
                video_playing = True

                # Get streamer frame
                raw_frame = self.streamer_outputs.get()

                # push to detector
                self.detector_pipe_parent_conn.send(raw_frame)

                # if detector has results continue..
                self.frame_counter += 1
                if self.frame_counter >= 2:

                    # Get Contours
                    final_frame, contours = self.detector_pipe_parent_conn.recv()

                    # push to viewport
                    self.viewport_inputs.put((final_frame,contours))

                continue

            # Start Exit Sequence
            if video_playing:

                self.stopFlag.set()
                self.streamer_proc.join()
                self.detector_proc.join()
                self.viewport_proc.join()

                break

        # gracefully exit!
        exit()



if __name__ == '__main__':

    # config path
    import os
    config_path = os.path.join(os.path.dirname(os.getcwd()),'Config','config.yaml')

    # Run app
    app = Application(config_path=config_path)
    app.work()