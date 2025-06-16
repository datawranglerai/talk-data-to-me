import pyaudio
import threading
import queue
import time


class AudioBuffer:
    def __init__(self):
        self.audio_queue = queue.Queue()
        self.is_playing = False
        self.stream = None
        self.p = None

    def start_stream(self):
        """Initialize and start the audio stream."""
        if self.p is None:
            self.p = pyaudio.PyAudio()
            self.stream = self.p.open(
                format=pyaudio.paInt16,
                channels=1,
                rate=24000,  # Gemini Live outputs at 24kHz[2]
                output=True,
                frames_per_buffer=4096,  # Larger buffer for smoother playback[4]
            )

        if not self.is_playing:
            self.is_playing = True
            self.playback_thread = threading.Thread(target=self._playback_worker, daemon=True)
            self.playback_thread.start()

    def add_audio_chunk(self, audio_bytes: bytes):
        """Add audio chunk to the playback queue."""
        self.audio_queue.put(audio_bytes)

    def _playback_worker(self):
        """Continuous playback worker thread."""
        while self.is_playing:
            try:
                # Get audio chunk with timeout to avoid blocking forever
                audio_chunk = self.audio_queue.get(timeout=0.1)
                if audio_chunk and self.stream:
                    self.stream.write(audio_chunk)
                self.audio_queue.task_done()
            except queue.Empty:
                # No audio available, brief pause
                time.sleep(0.01)
            except Exception as e:
                print(f"Audio playback error: {e}")

    def stop(self):
        """Stop audio playback and cleanup."""
        self.is_playing = False
        if hasattr(self, 'playback_thread'):
            self.playback_thread.join(timeout=1.0)
        if self.stream:
            self.stream.stop_stream()
            self.stream.close()
        if self.p:
            self.p.terminate()


# Global audio buffer instance
audio_buffer = AudioBuffer()
