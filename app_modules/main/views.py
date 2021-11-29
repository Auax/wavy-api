import json
import os
from dataclasses import asdict

from flask import Flask, request, jsonify
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS, cross_origin
from dotenv import load_dotenv

from app_modules.util.rooms import Room, Rooms
from app_modules.util.logger import log
from app_modules.util.captcha import verify_captcha

load_dotenv()

app = Flask(__name__, static_folder="/client/build")
app.config['SECRET_KEY'] = os.getenv("app_key")
app.config['CORS_HEADERS'] = "Content-Type"
ALLOWED_ORIGINS = os.getenv("ALLOWED_ORIGINS")

cors = CORS(app, resources={
    "/*": {"origins": ALLOWED_ORIGINS}}, support_credentials=True)

# You can enable logger and engineio_logger for debugging purposes
socketio = SocketIO(app,
                    cors_allowed_origins=ALLOWED_ORIGINS,
                    logger=False,
                    engineio_logger=False,
                    cors_credentials=True)

rooms = Rooms()


@app.route('/api/rooms')
@cross_origin(supports_credentials=True)
def home():
    return {"rooms": rooms.secure_api} if rooms.secure_api else {"200": "No Rooms"}


@app.route('/api/create/post', methods=['POST', 'GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def create_room():
    """
    API endpoint to validate and check the room form
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        room_name_ = request_data.get("name")
        room_description_ = request_data.get("description")
        is_private_ = request_data.get("is_private")
        password_ = request_data.get("password")
        captcha_token_ = request_data.get("captcha_token")

        captcha_res = verify_captcha(captcha_token_)
        if captcha_res["success"]:
            # Check if captcha score is higher than 0.7 (ranges from 0.0 to 1.0)
            if captcha_res["score"] > 0.7:
                if room_name_:
                    if is_private_ and len(password_) < 4:
                        return {"400": "The password must be at least 4 characters!"}

                    if not is_private_ and password_:
                        password_ = None

                    if len(room_name_) > 30 or len(room_description_) > 150 or len(password_) > 200:
                        return {"400": "Too long input values!"}

                    room = Room(
                        room_name_,
                        room_description_,
                        is_private_,
                        password_
                    )

                    rooms.add(asdict(room))
                    return {"200": room.id}

                else:
                    return {"400": "Please fill the correct values!"}
            else:
                return {"400": f"Captcha score is too low to determine you are human. Score = {captcha_res['score']}"}
        else:
            return {"400": "Captcha error!"}
    return {"400": "Method is not POST."}


@app.route("/api/validate/", methods=['POST', 'GET', 'OPTIONS'])
@cross_origin(supports_credentials=True)
def validate_user():
    """
    API endpoint for creating a username
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        username = request_data.get('username')
        password = request_data.get('password')
        room_id = request_data.get("room")

        log("/api/validate", request_data, 2)

        if not username:
            return {"400": "Invalid username."}
        if len(username) > 50:
            return {"400": "The username must be less than 50 characters."}

        if room := rooms.get(room_id):
            room_id = room["id"]
            if room.get("private"):
                if room.get("password") == password:
                    if not rooms.add_username(username, room_id):
                        return {"400": "The username already exists in this room."}
                    log("/api/validate", "Success!", 1)
                    return {"200": "Success"}
                return {"403": "Invalid password"}
            if rooms.add_username(username, room_id):
                log("/api/validate", "Success!", 1)
                return {"200": "Success"}
            else:
                return {"400": "The username already exists in this room."}
        return {"404": "Room not found"}

    else:
        return {"400": "Invalid method!"}


@app.route("/api/room/<int:id>")
def room_info(id):
    room = rooms.get(id, secure=True)
    return {"200": room} if room else {"404": "No room found"}


@app.route('/api/join', methods=['POST', 'GET'])
def join():
    """
    API endpoint to join a room.
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        room_id = request_data.get('id')
        password = request_data.get('password')

        if room := rooms.get(room_id):
            if room.get("private"):
                if room.get("password") == password:
                    log("/api/join", "Success!")
                    return {"200": "Success"}
                return {"403": "Invalid password"}
            log("/api/join", "Success!")
            return {"200": "Success"}
        return {"404": "Room not found"}
    return {"400": "Invalid method!"}


@socketio.on("join")
def on_join(data):
    sid = request.sid
    # Room ID
    channel = data["channel"]

    log("socketio join", f"DATA={data} SID={sid}")

    if rooms.is_private(channel):
        if rooms.get(channel)["password"] == data["password"]:
            join_room(channel)
        else:
            return {"403": "Invalid Password"}
    join_room(channel)
    return {"200": "OK"}


@socketio.on("message")
def handle_message(data):
    try:
        channel = data["channel"]
        message = data["message"]
        username = data["username"]
    except KeyError:
        return False

    log("incoming message", f"USER={username} ROOM={channel} MESSAGE={message}", mode=1)

    if 5000 >= len(message) > 0:
        emit('message', [message, username], room=channel)


@socketio.on("disconnect_client")
def disconnect(data):
    log("disconnect client", f"DATA={data}")
    room_id = data["room"]
    rooms.remove_username(data["username"], room_id)
    leave_room(room_id)
