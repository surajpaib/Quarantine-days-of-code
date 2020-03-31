import pyaudio
from prompt_toolkit.shortcuts import radiolist_dialog, input_dialog, message_dialog
import tempfile
import wave

class AudioRecorder:
    def __init__(self):
        self.audio_plugin = pyaudio.PyAudio()

        # Get user input on different parameters
        self.select_audio_device()
        self.set_recording_info()

    def __call__(self):
        self.filename = tempfile.TemporaryFile()
        # Begin recording process
        self.start_recording()
        self.stop_recording()

        #Save recording output
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

        self.chunk = 1024  # Record in chunks of 1024 samples
        self.sample_format = pyaudio.paInt16  # 16 bits per sample
        self.channels = 2
        self.fs = 44100  # Record at 44100 samples per second

        print('Initializing Stream')

        self.stream = self.audio_plugin.open(format=self.sample_format,
                        channels=self.channels,
                        rate=self.fs,
                        frames_per_buffer=self.chunk,
                input=True, input_device_index=self.selected_device, stream_callback=self.callback_function())      
    

    def callback_function(self):
        def callback(in_data, frame_count, time_info, status):
            self.audio_frames.append(in_data)
            return in_data, pyaudio.paContinue
        return callback

    def start_recording(self):
        """
        Begin recording on dialog accept
        """
        self.audio_frames = []
        message_dialog(
            title='Start Recording',
            text='Do you want to start recording?\n').run()

        self.stream.start_stream()


    def stop_recording(self):
        """
        Destroy stream objects
        """
        message_dialog(
            title='Recording ..',
            text='Click OK when you want to stop recording\n').run()
        self.stream.stop_stream()
        self.stream.close()
        self.audio_plugin.terminate()        

    def save_recording(self):
        """
        Save recording, open dialog for filename
        """
        self.filename = input_dialog(
            title='Save recording',
            text='Enter filename to save recording, *.wav').run()

        if self.filename is not None:
            wf = wave.open("{}.wav".format(self.filename), 'wb')
            wf.setnchannels(self.channels)
            wf.setsampwidth(self.audio_plugin.get_sample_size(self.sample_format))
            wf.setframerate(self.fs)
            wf.writeframes(b''.join(self.audio_frames))
            wf.close()

if __name__ == "__main__":
    audio_recorder = AudioRecorder()
    audio_recorder()