import whisper
import tempfile
import os
from fastapi import UploadFile

# Whisper model (सुरुवातीला एकदाच load होईल)
model = whisper.load_model("base")

async def process_voice_input(audio: UploadFile):
    try:
        # File extension check
        file_ext = os.path.splitext(audio.filename)[-1].lower()
        if file_ext not in [".mp3", ".mp4", ".m4a", ".wav"]:
            raise ValueError("Unsupported file format: " + file_ext)

        # Save temp audio file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_ext) as tmp:
            tmp.write(await audio.read())
            tmp_path = tmp.name

        # Transcribe
        result = model.transcribe(tmp_path)
        return {"text": result["text"]}

    except Exception as e:
        return {"error": str(e)}
    finally:
        try:
            os.remove(tmp_path)
        except:
            pass
