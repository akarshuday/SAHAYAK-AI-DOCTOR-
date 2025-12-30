from gtts import gTTS
from elevenlabs.client import ElevenLabs
import elevenlabs
from elevenlabs.core.api_error import ApiError
from pydub import AudioSegment
import os
import platform
import subprocess
from dotenv import load_dotenv

# Load environment variables
load_dotenv()
ELEVENLABS_API_KEY = os.environ.get("ELEVENLABS_API_KEY") or os.environ.get("ELEVEN_API_KEY")

def play_audio(filepath):
    os_name = platform.system()
    if os_name == "Windows":
        try:
            subprocess.run(['ffplay', '-nodisp', '-autoexit', filepath], check=True)
        except Exception:
            ps = (
                f"$player = New-Object -ComObject WMPlayer.OCX; "
                f"$player.URL = '{filepath}'; "
                f"$player.controls.play(); "
                f"$duration = [math]::Ceiling($player.currentMedia.duration); "
                f"Start-Sleep -Seconds $duration; "
                f"$player.controls.stop();"
            )
            subprocess.run(['powershell', '-c', ps])
    elif os_name == "Darwin":
        subprocess.run(['afplay', filepath])
    elif os_name == "Linux":
        try:
            subprocess.run(['ffplay', '-nodisp', '-autoexit', filepath], check=True)
        except Exception:
            try:
                subprocess.run(['mpg123', filepath], check=True)
            except Exception as e:
                print(f"Audio playback failed: {e}")

def text_to_speech_with_gtts(text, output_mp3="gtts_output.mp3"):
    tts = gTTS(text=text, lang="en")
    tts.save(output_mp3)
    play_audio(output_mp3)
    return output_mp3

def text_to_speech_with_elevenlabs(text, output_mp3="elevenlabs_output.mp3", voice="Aria"):
    try:
        if not ELEVENLABS_API_KEY:
            return text_to_speech_with_gtts(text, output_mp3)
        client = ElevenLabs(api_key=ELEVENLABS_API_KEY)
        audio = client.generate(
            text=text,
            voice=voice,
            output_format="mp3_22050_32",
            model="eleven_turbo_v2"
        )
        elevenlabs.save(audio, output_mp3)
        play_audio(output_mp3)
        return output_mp3
    except ApiError:
        return text_to_speech_with_gtts(text, output_mp3)
    except Exception:
        return text_to_speech_with_gtts(text, output_mp3)

# =====================
# Example usage
# =====================
if __name__ == "__main__":
    sample_text = "Hello, I am your AI doctor! Testing audio playback."
    
    text_to_speech_with_gtts(sample_text)
    
    text_to_speech_with_elevenlabs(sample_text)
