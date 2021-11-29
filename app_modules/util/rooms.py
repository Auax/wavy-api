import copy
import random
import string
from .logger import log
from dataclasses import dataclass, field
from typing import Any, Union


@dataclass(frozen=True, order=True)
class Room:
    name: str
    description: str = ""
    private: bool = False
    password: str = ""
    id: str = field(default_factory=lambda: "".join(
        random.choices(string.digits, k=12)))


class Rooms:
    def __init__(self):
        self._chain = []
        self._secure_api = []

    @property
    def chain(self):
        return self._chain

    @property
    def secure_api(self):
        secure = []
        for room in copy.deepcopy(self.chain):
            try:
                room.pop("password")
            except KeyError:
                pass
            secure.append(room)

        return secure

    def get(self, room_id: Any, secure: bool = False) -> Union[Room, None]:
        chain = self.secure_api if secure else self.chain
        for room in chain:
            if room["id"] == str(room_id):
                return room

    def add(self, value: Any):
        self.chain.append(value)

    def add_username(self, username: str, room_id: str) -> bool:
        # Get the room by ID
        room = self.get(room_id)
        if room_usernames := room.get("usernames"):
            log("usernames", str(room_usernames), 2)
            for room_username in room_usernames:
                log("username", str(room_username), 2)
                if room_username != username:
                    room["usernames"] = []
                    log("true", True, 2)
                    room["usernames"].append(username)
                    return True
        else:
            # No users in room
            # Can register the user directly
            room["usernames"] = []
            room["usernames"].append(username)
            return True

        return False

    def remove_username(self, username: str, room_id: str) -> bool:
        room = self.get(room_id)
        try:
            room["usernames"].remove(username)
            return True
        except KeyError or ValueError:
            return False

    def is_private(self, room_id) -> bool:
        room = self.get(room_id)
        return room["private"]
