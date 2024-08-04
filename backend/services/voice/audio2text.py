from tempfile import NamedTemporaryFile
import openai
from config import OPENAI_API_KEY

openai.api_key = OPENAI_API_KEY

def transcribe_audio_to_text(audio_bytes):
    with NamedTemporaryFile(delete=True, suffix=".wav") as temp_file:
        temp_file.write(audio_bytes)
        temp_file.flush()
        with open(temp_file.name, "rb") as audio_file:
            response = openai.audio.transcriptions.create(
                model="whisper-1", 
                file=audio_file
                )
    return response.text