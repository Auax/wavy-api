import json
from dataclasses import asdict

from flask import Flask, request
from flask_socketio import SocketIO, emit, join_room, leave_room
from flask_cors import CORS

from app_modules.util.rooms import Room, Rooms
from app_modules.util.logger import log
from app_modules.util.captcha import verify_captcha

app = Flask(__name__, static_folder="/client/build")
app.config['SECRET_KEY'] = "h3QfpgYepU43mHu4"

cors = CORS(app, resources={r"/api/*": {"origins": ["http://localhost:3000", "https://auax.github.io"]}})

# Enable logger and engineio_logger for debug purposes
socketio = SocketIO(app, cors_allowed_origins="https://auax.github.io",
                    logger=False, engineio_logger=False)

rooms = Rooms()


@app.route('/api/rooms')
def home():
    return {"rooms": rooms.secure_api} if rooms.secure_api else ""


@app.route('/api/create/post', methods=['POST', 'GET'])
def create_room():
    """API endpoint to validate and check the room form
    """
    if request.method == 'POST':
        request_data = json.loads(request.data)
        room_name_ = request_data.get("name")
        room_description_ = request_data.get("description")
        is_private_ = request_data.get("is_private")
        password_ = request_data.get("password")
        captcha_token_ = request_data.get("captcha_token")

        captcha_res = verify_captcha(captcha_token_)
        print(captcha_res)
        print(captcha_res["score"])
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
                return {"400": "Captcha score is too low to determine you are human."}
        else:
            return {"400": "Captcha error!"}
    return {"400": "Method is not POST."}


@app.route("/api/create/username", methods=['POST', 'GET'])
def create_user():
    """API endpoint for creating a username"""
    if request.method == 'POST':
        request_data = json.loads(request.data)
        username = request_data.get('username')
        room = request_data.get("room")

        if not username:
            return {"400": "Invalid username."}
        if len(username) > 50:
            return {"400": "The username must be less than 50 characters."}

        if not rooms.add_username(username, room):
            return {"400": "The username already exists in this room."}

        log("/api/create/username", f"USER={username} ROOM={room}")
        return {"200": "ok"}

    else:
        return {"400": "Please fill the correct values!"}


@socketio.on("join")
def on_join(data):
    sid = request.sid

    log("join", f"DATA={data} SID={sid}")

    channel = data["channel"]
    join_room(channel)


@socketio.on("message")
def handle_message(data):
    try:
        channel = data["channel"]
        message = data["message"]
        username = data["username"]
    except KeyError:
        return False

    log("incoming message",
        f"USER={username} ROOM={channel} MESSAGE={message}")

    if 5000 >= len(message) > 0:
        emit('message', [message, username], room=channel)


@socketio.on("disconnect_client")
def disconnect(data):
    log("disconnect client", f"DATA={data}")
    room_id = data["room"]
    rooms.remove_username(data["username"], room_id)
    leave_room(room_id)
