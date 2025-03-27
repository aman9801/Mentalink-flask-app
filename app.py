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


@socketio.on("av_stream")
def handle_av_stream(data):
    # Broadcast the received audio-video data to all clients except the sender
    emit("av_stream", data, broadcast=True, include_self=False)


@socketio.on("disconnect")
def handle_disconnect():
    print("Client disconnected")


if __name__ == "__main__":
    socketio.run(app, port=5000)
