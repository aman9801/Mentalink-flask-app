import tempfile
from flask import Flask
from flask_socketio import SocketIO, emit
from flask_cors import CORS
from flask import Response, request

app = Flask(__name__)

CORS(app, resources={r"/*": {"origins": "*"}}, supports_credentials=True)


socketio = SocketIO(app, cors_allowed_origins="*")


@app.before_request
def basic_authentication():
    if request.method.lower() == 'options':
        return Response()

@app.route('/')
def hello():
    return "Hello World!"

@socketio.on("connect")
def handle_connect():
    print("Client connected")

import io
import base64
import soundfile as sf
import librosa
from pydub import AudioSegment


def decode_webm_audio(audio_base64):
    try:
        audio_bytes = base64.b64decode(audio_base64)
        webm_stream = io.BytesIO(audio_bytes)

        # Convert WebM to WAV using pydub
        audio_segment = AudioSegment.from_file(webm_stream, format="webm")

        # Optional: export to raw PCM
        wav_io = io.BytesIO()
        audio_segment.export(wav_io, format="wav")
        wav_io.seek(0)

        # For librosa / numpy processing
        import soundfile as sf
        y, sr = sf.read(wav_io)
        return y, sr

    except Exception as e:
        print(f"❌ Audio decoding failed: {e}")
        return None, None


def safe_decode_and_load_audio(audio_base64: str, target_sr=16000):
    try:
        # Decode base64 safely
        try:
            audio_bytes_padded = audio_base64 + "=" * (-len(audio_base64) % 4)
            audio_bytes = base64.b64decode(audio_bytes_padded, validate=True)
        except base64.binascii.Error as e:
            print(f"[decode] Base64 decode failed: {e}")
            return None, None

        # Trim to nearest multiple of 2 bytes (16-bit PCM)
        # safe_len = (len(audio_bytes) // 2) * 2
        # audio_bytes = audio_bytes[:safe_len]

        

        # # Try reading with soundfile first
        # try:
        #     y, sr = sf.read(audio_file)
        #     if sr != target_sr:
        #         y = librosa.resample(y.T if y.ndim > 1 else y, orig_sr=sr, target_sr=target_sr)
        #         sr = target_sr
        #     print(f"[soundfile] Loaded audio: shape={y.shape}, sr={sr}")
        #     return y, sr
        # except Exception as e_sf:
        #     print(f"[soundfile] Failed: {e_sf}")
        #     audio_file.seek(0)

        try:
            # first write it as a wav file with tempfile
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as temp_wav:
                temp_wav.write(audio_bytes)
                temp_wav.seek(0)
                temp_path = temp_wav.name
                print(f"Temp wav file created: {temp_wav.name}")
                y, sr = librosa.load(temp_path, sr=None)
            # with io.BytesIO(audio_bytes) as audio_file:
                #y, sr = librosa.load(audio_file, sr=target_sr)
            print(f"[librosa] Loaded audio: shape={y.shape}, sr={sr}")
            return y, sr
        except Exception as e_lb:
            print(f"[librosa] Failed: {e_lb}")
            return None, None

    except Exception as e:
        print(f"[unknown] Unexpected failure: {e}")
        return None, None

@socketio.on("av_stream")
def handle_av_stream(data):
    # This audio is comming as base64 string convert it into wave bytes
    audio_data = data['audio']
    video_data = data['image']
    
    y, sr = safe_decode_and_load_audio(audio_data)
    if y is None:
       print("Failed to decode audio")
       return
    
    # Decode the base64 audio data
    audio_bytes = base64.b64decode(audio_data)

    # Wrap in BytesIO directly
    # with io.BytesIO(audio_bytes[:(len(audio_bytes)//4)*4]) as audio_file:
        # y, sr = librosa.load(audio_file, sr=16000)
        # print(f"Audio sample rate: {sr}")


    # with open(audio_file, 'wb') as f:
        # y, sr = librosa.load(audio_file, sr=16000)
    print(f"Audio shape: {y.shape}, Sample Rate: {sr}")
    emit("av_stream", data, broadcast=True, include_self=False)


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")

import os

port = int(os.getenv("PORT", 10000))

if __name__ == "__main__":
    socketio.run(app, host='0.0.0.0',  port=port)
