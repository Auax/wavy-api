import random
import string
from dataclasses import dataclass, field
from typing import Any


class Rooms:
    def __init__(self):
        self._chain = []
        self._secure_api = []

    @property
    def chain(self):
        return self._chain

    @property
    def secure_api(self):
        secure_api = []
        for room in self.chain:
            room.pop("password", None)
            secure_api.append(room)

        return secure_api

    def add(self, value: Any):
        self.chain.append(value)

    def add_username(self, username: str, room_id: str) -> bool:
        for room in self.chain:
            if room["id"] == room_id:
                if room_usernames := room.get("usernames"):
                    for room_username in room_usernames:
                        if room_username != username:
                            room["usernames"] = []
                            room["usernames"].append(username)
                            return True
                else:
                    room["usernames"] = []
                    room["usernames"].append(username)
                    return True
        return False

    def remove_username(self, username: str, room_id: str) -> bool:
        for room in self.chain:
            if room["id"] == room_id:
                try:
                    room["usernames"].remove(username)
                    return True
                except KeyError:
                    return False


@dataclass(frozen=True, order=True)
class Room:
    name: str
    description: str = ""
    private: bool = False
    password: str = ""
    id: str = field(default_factory=lambda: "".join(
        random.choices(string.digits, k=12)))
