import pyautogui
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
import cv2
import threading
import tempfile
import numpy as np
import time
import os

class ScreenGrabber:
    def __init__(self):
        self.set_recording_info()


    def set_recording_info(self):
        """
        Set info for stream recorder
        """
        self.screenWidth, self.screenHeight = pyautogui.size()
        print(self.screenWidth, self.screenHeight)
        self.filename = 'intermediate.mp4'
        self.channels = 3
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')
        print('Initializing Stream')

        self.stream = cv2.VideoWriter(self.filename, fourcc, 10, (int(self.screenWidth), int(self.screenHeight)))


    def record(self):
        # Begin recording process
        self.start_recording()


    def terminate(self):
        self._recording = False


    def start_recording(self):
        """
        Begin recording on dialog accept
        """
      
        self._recording = True
        time.sleep(0.5)
        while self._recording:
            screen = np.asarray(pyautogui.screenshot())
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            self.stream.write(screen)

    def stop_recording(self):
        """
        Destroy stream objects
        """
        message_dialog(
            title='Recording ..',
            text='Click OK when you want to stop recording\n').run()

        self.terminate()


    def save_recording(self):
        """
        Save recording, open dialog for filename
        """
        self.filename = input_dialog(
            title='Save recording',
            text='Enter filename to save recording, *.mp4').run()

        if self.filename is not None:
            os.rename("intermediate.mp4", "{}.mp4".format(self.filename))
        else:
            os.remove("intermediate.mp4")


    def __call__(self):
        screen_thread = threading.Thread(target=self.record)

        # Initialize Recording Prompt
        message_dialog(
            title='Start Recording',
            text='Do you want to start recording?\n').run()
        screen_thread.start()

        self.stop_recording()
        screen_thread.join()
        self.stream.release()
        self.save_recording()


if __name__ == "__main__":
    screengrab = ScreenGrabber()
    screengrab()
