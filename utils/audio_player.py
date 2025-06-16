import pyaudio
import queue
import atexit


class CallbackAudioPlayer:
    def __init__(self):
        self.audio_queue = queue.Queue(maxsize=100)  # Limit queue size to prevent memory issues
        self.p = None
        self.stream = None
        self.is_running = False

    def start(self):
        """Initialize and start the audio stream."""
        if not self.is_running:
            try:
                self.p = pyaudio.PyAudio()

                # Use callback for continuous playback
                self.stream = self.p.open(
                    format=pyaudio.paInt16,
                    channels=1,
                    rate=24000,  # Gemini Live outputs at 24kHz
                    output=True,
                    frames_per_buffer=1024,
                    stream_callback=self._audio_callback
                )

                self.stream.start_stream()
                self.is_running = True
                print("🔊 Audio player started successfully")
            except Exception as e:
                print(f"Failed to start audio player: {e}")

    def _audio_callback(self, in_data, frame_count, time_info, status):
        """Callback function for continuous audio playback."""
        bytes_needed = frame_count * 2  # 2 bytes per sample for 16-bit

        try:
            # Try to get audio data from queue (non-blocking)
            data = self.audio_queue.get_nowait()

            # Handle data size mismatches
            if len(data) < bytes_needed:
                # Pad with silence if too short
                data += b'\x00' * (bytes_needed - len(data))
            elif len(data) > bytes_needed:
                # Truncate if too long, put remainder back in queue
                remainder = data[bytes_needed:]
                data = data[:bytes_needed]
                # Put remainder back at front of queue for next callback
                try:
                    temp_queue = queue.Queue()
                    temp_queue.put(remainder)
                    while not self.audio_queue.empty():
                        temp_queue.put(self.audio_queue.get_nowait())
                    self.audio_queue = temp_queue
                except:
                    pass  # If queue operations fail, just continue

            return (data, pyaudio.paContinue)

        except queue.Empty:
            # No data available, play silence
            silence = b'\x00' * bytes_needed
            return (silence, pyaudio.paContinue)
        except Exception as e:
            print(f"Audio callback error: {e}")
            silence = b'\x00' * bytes_needed
            return (silence, pyaudio.paContinue)

    def add_chunk(self, audio_bytes: bytes):
        """Add audio chunk to playback queue."""
        try:
            # Add chunk to queue (non-blocking)
            self.audio_queue.put_nowait(audio_bytes)
        except queue.Full:
            # Queue is full, remove oldest item and add new one
            try:
                self.audio_queue.get_nowait()  # Remove oldest
                self.audio_queue.put_nowait(audio_bytes)  # Add new
            except queue.Empty:
                pass
        except Exception as e:
            print(f"Failed to add audio chunk: {e}")

    def stop(self):
        """Stop and cleanup audio resources."""
        if self.is_running:
            self.is_running = False
            try:
                if self.stream:
                    self.stream.stop_stream()
                    self.stream.close()
                if self.p:
                    self.p.terminate()
                print("🔊 Audio player stopped")
            except Exception as e:
                print(f"Error stopping audio player: {e}")


# Global audio player instance
_audio_player = CallbackAudioPlayer()
atexit.register(_audio_player.stop)  # Cleanup on exit
