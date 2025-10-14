# utils/stt_utils.py
import whisper
import tempfile
import os
from pydub import AudioSegment

# Load Whisper model once (choose 'tiny' or 'base' for CPU speed; 'small'/'medium' for better accuracy)
# For CPU: 'tiny' or 'base' recommended. If you have GPU, change to 'small' or 'medium'.
_WHISPER_MODEL_NAME = os.environ.get("WHISPER_MODEL", "base")
_model = None

def _load_model():
    global _model
    if _model is None:
        print(f"Loading Whisper model: {_WHISPER_MODEL_NAME} (this may take a while)...")
        _model = whisper.load_model(_WHISPER_MODEL_NAME)
    return _model

def _ensure_wav(path_in, path_out):
    """
    Convert to 16kHz mono WAV using pydub/ffmpeg (Whisper works with many formats but this ensures compatibility).
    """
    try:
        audio = AudioSegment.from_file(path_in)
        audio = audio.set_frame_rate(16000).set_channels(1)
        audio.export(path_out, format="wav")
        return path_out
    except Exception as e:
        # If conversion fails, just return original
        return path_in

def transcribe_offline(uploaded_file, model_name=None):
    """
    uploaded_file: Streamlit UploadedFile or file-like with getbuffer()
    Returns: transcript string
    """
    model_to_use = model_name or _WHISPER_MODEL_NAME
    global _model
    if _model is None:
        _model = whisper.load_model(model_to_use)

    # Save uploaded file to temp file
    tf = tempfile.NamedTemporaryFile(suffix=os.path.splitext(getattr(uploaded_file, "name", "audio.wav"))[-1], delete=False)
    tf.write(uploaded_file.getbuffer())
    tf.close()
    tmp_in = tf.name

    # Convert to WAV 16k mono
    tmp_wav = tmp_in + ".wav"
    tmp_wav = _ensure_wav(tmp_in, tmp_wav)

    # transcribe
    result = _model.transcribe(tmp_wav, fp16=False)  # fp16=False for CPU
    text = result.get("text", "").strip()

    # cleanup
    try:
        os.remove(tmp_in)
    except Exception:
        pass
    try:
        if tmp_wav != tmp_in:
            os.remove(tmp_wav)
    except Exception:
        pass

    return text
