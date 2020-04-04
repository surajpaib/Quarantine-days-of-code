import pyaudio
import pyautogui
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
import tempfile
import wave
import threading
import cv2
import numpy as np
import time
import os
from mhmovie.code import *

class ScreenRecorder:
    def __init__(self):
        self.audio_plugin = pyaudio.PyAudio()

        # Get user input on different parameters
        self.select_audio_device()
        self.set_recording_info()

    def audio_record(self):
        # Begin recording process
        self.start_audio_recording()

    def screen_record(self):
        # Begin recording process
        self.start_screen_recording()

    def __call__(self):
        message_dialog(
            title='Start Recording',
            text='Do you want to start recording?\n').run()
        audio_thread = threading.Thread(target=self.audio_record)
        screen_thread = threading.Thread(target=self.screen_record)

        audio_thread.start()
        screen_thread.start()

        message_dialog(
            title='Recording ..',
            text='Click OK when you want to stop recording\n').run()

        self.stop_screen_recording() 
        screen_thread.join()
           
        self.stop_audio_recording()
        audio_thread.join()
  

        self.screen_stream.release()
        self.save_recording()

    def select_audio_device(self):
        """
        Select Audio Device from list of available microphones. Check based on input channels.
        """
        info = self.audio_plugin.get_host_api_info_by_index(0)
        numdevices = info.get('deviceCount')
        available_audio_devices = []
        for i in range(0, numdevices):
                if (self.audio_plugin.get_device_info_by_host_api_device_index(0, i).get('maxInputChannels')) > 0:
                    available_audio_devices.append((i, self.audio_plugin.get_device_info_by_host_api_device_index(0, i).get('name')))

        self.selected_device = radiolist_dialog(
            title='Microphone Selector',
            text='Select your microphone to record',
            values=available_audio_devices,
        ).run()

        print("Selected Device ID:", self.selected_device)


    def set_recording_info(self):
        """
        Set info for stream recorder
        """

        # Audio Stream
        self.audio_frames = []

        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second


        self.audio_stream = self.audio_plugin.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                input=True, input_device_index=self.selected_device, stream_callback=self.callback_function())      
        
        # Screen Capture stream
        self.screenWidth, self.screenHeight = pyautogui.size()
        print(self.screenWidth, self.screenHeight)
        self.filename = 'intermediate.mp4'
        fourcc = cv2.VideoWriter_fourcc(*'mp4v')

        self.screen_stream = cv2.VideoWriter(self.filename, fourcc, 10, (int(self.screenWidth), int(self.screenHeight)))
        print('Initializing Stream')


    def terminate(self):
        self._recording = False

    def callback_function(self):
        def callback(in_data, frame_count, time_info, status):
            self.audio_frames.append(in_data)
            return in_data, pyaudio.paContinue
        return callback

    def start_audio_recording(self):
        """
        Begin recording on dialog accept
        """
        self.audio_stream.start_stream()

    def start_screen_recording(self):
        """
        Begin recording on dialog accept
        """
      
        self._recording = True
        time.sleep(0.5)
        while self._recording:
            screen = np.asarray(pyautogui.screenshot())
            screen = cv2.cvtColor(screen, cv2.COLOR_BGR2RGB)
            self.screen_stream.write(screen)


    def stop_audio_recording(self):
        """
        Destroy stream objects
        """

        self.audio_stream.stop_stream()
        self.audio_stream.close()
        self.audio_plugin.terminate()        

    def stop_screen_recording(self):
        """
        Destroy stream objects
        """

        self.terminate()

    def save_recording(self):
        """
        Save recording, open dialog for filename
        """
        self.filename = input_dialog(
            title='Save recording',
            text='Enter filename to save recording, *.mp4').run()

        if self.filename is not None:
            wf = wave.open("intermediate.wav", 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio_plugin.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()
        else:
            os.remove("intermediate.wav")
            os.remove("intermediate.mp4")
            exit()

        try:
            screen = movie("intermediate.mp4")
            audio = music("intermediate.wav")
            audio.Aconvert()#convert wav to mp3
            video = screen + audio
            video.save("{}.mp4".format(self.filename))
            input_dialog(
                title='Saved!',
                text='Your file has been saved to the location!').run()
        except:
            input_dialog(
                title='Error!',
                text='Error with saving, please contact developer').run()

if __name__ == "__main__":
    screen_recorder = ScreenRecorder()
    screen_recorder()