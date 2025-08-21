#!/usr/bin/env python3

import enum
import struct


class MessageTypes(enum.IntEnum):
    REQ_REGISTER = 1
    REQ_NEW_GAME = enum.auto()
    REQ_SAVE_GAME = enum.auto()
    REQ_LOAD_GAME = enum.auto()
    REQ_MOVE = enum.auto()
    REQ_GET_LEVEL = enum.auto()
    RESP_STANDARD = 64
    RESP_REGISTERED = enum.auto()
    RESP_LEVEL = enum.auto()
    RESP_WIN = enum.auto()
    RESP_LOSE = enum.auto()
    RESP_ERROR = enum.auto()


class Message:
    """Message class that packages payloads"""

    def __init__(self, mtype: MessageTypes, *args : tuple) -> None:
        """
        mtype represents message codes and communication between the client and server
        args can represent either a tuple orn othing at all dependent on the command ran by the user
        This class is used to represent struct packing and unpacking for the structure of the project which includes
        moves, registering users and more
        """

        self.mtype : MessageTypes = mtype
        self.header : str = "!BB"
        self.args : tuple = args


    def serialize(self) -> bytes:
        """Function that packs payload and sends it to the server"""
        try:
            match self.mtype:

                case MessageTypes.REQ_REGISTER.value:
                    username, *_ = self.args
                    enc_user = username.encode()
                    payload = struct.pack(f"{len(enc_user)}s", enc_user)
                    return struct.pack(f"{self.header}{len(payload)}s", self.mtype, len(payload), payload)

                case MessageTypes.REQ_NEW_GAME.value:

                    newgame_name, *_ = self.args
                    encoded_name = newgame_name.encode()
                    payload_n = struct.pack(f"{len(encoded_name)}s", encoded_name)
                    return struct.pack(f"{self.header}{len(payload_n)}s", self.mtype, len(payload_n), payload_n)

                case MessageTypes.REQ_SAVE_GAME.value:
                    
                    return struct.pack(f"{self.header}", self.mtype, 0)
                
                case MessageTypes.REQ_LOAD_GAME.value:
                    loadname, *_ = self.args
                    encoded_loadname = loadname.encode()
                    payload_l = struct.pack(f"{len(encoded_loadname)}s", encoded_loadname)
                    return struct.pack(f"{self.header}{len(payload_l)}s", self.mtype, len(payload_l), payload_l)
                
                case MessageTypes.REQ_GET_LEVEL.value:

                    return struct.pack(f"{self.header}", self.mtype, 0)
                
                case MessageTypes.REQ_MOVE.value:
                    move, *_ = self.args
                    enc_move = move.encode()
                    payload_m = struct.pack(f"{len(enc_move)}s", enc_move)
                    return struct.pack(f"{self.header}{len(payload_m)}s", self.mtype, len(payload_m), payload_m)

                case _:
                    raise OSError("Err : Unknown Message Type")
                
        except OSError as e:
            print(e.with_traceback(e.__traceback__))
            return b''

    @staticmethod
    def deserialize(buffer : bytes) -> tuple:
        """Deserialize buffer received"""

        response_header = "!BB"
        response_level = '101s'
        try:
            if len(buffer) == 0:
                return MessageTypes.RESP_ERROR.value, "Error Occured Unpacking"
            mtype, mlen = struct.unpack_from(f"{response_header}", buffer, offset = 0)

            match mtype:

                case MessageTypes.RESP_REGISTERED.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{len(buffer) - 2}s", buffer)
                    return mtype, mdata
                
                case MessageTypes.RESP_STANDARD.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{len(buffer) - 2}s", buffer)
                    return mtype, mdata
                
                case MessageTypes.RESP_LEVEL.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{response_level}", buffer)
                    return mtype, mdata
                
                case MessageTypes.RESP_LOSE.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{len(buffer) - 2}s", buffer)
                    return mtype, mdata

                case MessageTypes.RESP_WIN.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{len(buffer) - 2}s", buffer)
                    return mtype, mdata

                case MessageTypes.RESP_ERROR.value:

                    mtype, _, mdata = struct.unpack(f"{response_header}{len(buffer) - 2}s", buffer)
                    return mtype, mdata
                
                case _:

                    return MessageTypes.RESP_ERROR.value, "Error Occured Unpacking"
                
        except OSError as e:
            return MessageTypes.RESP_ERROR.value, "Error Occured Unpacking"



                    

