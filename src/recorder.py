import pyaudio
import wave
import logging

class Recorder(object):
    # A recorder class for recording audio to a WAV file.   Records in mono by default.
    
    def __init__(self, channels=1, rate=44100, frames_per_buffer=1024):
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer        

        self.logger = logging.getLogger(__name__)
        
        self.logger.info("__init__()> I/P channels= %s , rate= %s , frames_per_buffer= %s" % (self.channels, self.rate, self.frames_per_buffer))

    def open(self, fname, mode='wb'):
        self.logger.info("open()> Calling class RecordingFile")
        
        return RecordingFile(fname, mode, self.channels, self.rate, self.frames_per_buffer)

class RecordingFile(object):

    def __init__(self, fname, mode, channels, rate, frames_per_buffer):
        self.logger = logging.getLogger(__name__)
        self.fname = fname
        self.mode = mode
        self.channels = channels
        self.rate = rate
        self.frames_per_buffer = frames_per_buffer
        self._pa = pyaudio.PyAudio()
        self.wavefile = self._prepare_file(self.fname, self.mode)
        self._stream = None
        
        self.logger.info("__init__()> I/P fname= %s , mode= %s , channels= %s, rate= %s , frames_per_buffer= %s , _pa= %s , wavefile= %s , stream= %s" % (self.fname, self.mode, self.channels, self.rate, self.frames_per_buffer, self._pa, self.wavefile, self._stream))

    def __enter__(self):
        self.logger.info("__enter__()> returing self")
        return self

    def __exit__(self, exception, value, traceback):
        self.logger.info("__exit__()> self.close()")
        self.close()

    def record(self, duration):
        try:
            self.logger.info("record()> enter")
            # Use a stream with no callback function in blocking mode
            self._stream = self._pa.open(format=pyaudio.paInt16,
                                            channels=self.channels,
                                            rate=self.rate,
                                            input=True,
                                            frames_per_buffer=self.frames_per_buffer)
            for _ in range(int(self.rate / self.frames_per_buffer * duration)):
                audio = self._stream.read(self.frames_per_buffer)
                self.wavefile.writeframes(audio)
            self.logger.info("record()> exit")
            return None
        except Exception, e:
            self.logger.error("record()>", exc_info = True)

    def start_recording(self):
        try:
            self.logger.info("start_recording()> enter")
            # Use a stream with a callback in non-blocking mode
            self._stream = self._pa.open(format=pyaudio.paInt32,
                                            channels=self.channels,
                                            rate=self.rate,
                                            input=True,
                                            frames_per_buffer=self.frames_per_buffer,
                                            stream_callback=self.get_callback())
            self._stream.start_stream()
            self.logger.info("start_recording()> exit")
            return self
        except Exception, e:
            self.logger.error("start_recording()>", exc_info = True)

    def stop_recording(self):
        try:
            self._stream.stop_stream()
            self.logger.info("stop_recording()> Recording stopped")
            return self
        except Exception, e:
            self.logger.error("stop_recording()>", exc_info = True)

    def get_callback(self):
        try:
            self.logger.info("get_callback()> enter")
            def callback(in_data, frame_count, time_info, status):
                self.wavefile.writeframes(in_data)
                return in_data, pyaudio.paContinue
            self.logger.info("get_callback()> exit")
            return callback
        except Exception, e:
            self.logger.error("get_callback()>", exc_info = True)

    def close(self):     
        try:
            self._stream.close()
            self._pa.terminate()
            self.wavefile.close()
            self.logger.info("close()> Stream closed, _pa terminated, wavefile closed")
        except Exception, e:
            self.logger.error("close()>", exc_info = True)

    def _prepare_file(self, fname, mode='wb'):   
        wavefile = None
        try:
            self.logger.info("_prepare_file()> Enter")
            wavefile = wave.open(fname, mode)
            wavefile.setnchannels(self.channels)
            wavefile.setsampwidth(self._pa.get_sample_size(pyaudio.paInt32))
            wavefile.setframerate(self.rate)
            self.logger.info("_prepare_file()> Exit")
        except Exception, e:
            self.logger.error("_prepare_file()>", exc_info = True)
        finally:
            return wavefile