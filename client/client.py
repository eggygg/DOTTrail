#!/usr/bin/env python3

import cmd2
import re
import socket
import typing

from protocol import Message
from protocol import MessageTypes

BUFFER = 1024


class DotTrail(cmd2.Cmd):
    """A simple cmd2 client that connects to a server that allows playing the 'DOT Trail' """

    def __init__(self):
        super().__init__()
        self.prompt = "DOT Trail"
        self.socket = None
        self.register_ran = False

    def connection(self, ip : int | str, port : int):
        """Establishes a connection with the server via a socket connection"""
        try:
            if self.socket is not None:
                self.poutput("Attn : Connection Already Established")
                return False
            
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((ip, int(port)))
            self.poutput("Successfully Connected!")
            return True

        except OSError as e:
            self.poutput(e)
            self.socket = None
            return False
    def do_register(self, arg):
        """Registers the client with the server"""
        
        if self.register_ran:
            self.poutput("Already Registered and established connection!")
            return
        try:
            username, ip, port = DotTrail.validate_registration(arg)
            if (username is None) or (ip is None) or (port is None):

                self.poutput("Err : Invalid Registration. Try Again")
                return



            if not self.connection(ip, int(port)):
                
                self.poutput("Err : Connection failed")
                self.socket = None
                return

            packed_msg = Message(MessageTypes.REQ_REGISTER, username).serialize()

            if not self.send_packet(packed_msg):
                self.poutput("Failure to send msg to server")
                return

            recv_packet = self.recv_packet(BUFFER)

            if len(recv_packet) == 0:
                self.poutput("Nothing received from the server!")

            unpack_resp = Message.deserialize(recv_packet)
            
            if unpack_resp[0] == MessageTypes.RESP_ERROR:
                self.poutput(unpack_resp[1])
                return

            self.poutput(unpack_resp[0])
            self.poutput(unpack_resp[1])
            self.register_ran = True

        except OSError as e:
            self.poutput(e.with_traceback(e.__traceback__))

    def do_display(self, arg):
        """displays current board to user"""

        if not self.socket:
            self.poutput("Register before utilizing other commands")
            return
        
        try:
            packed_msg = Message(MessageTypes.REQ_GET_LEVEL).serialize()

            if not self.send_packet(packed_msg):
                self.poutput("Err : Failure to send msg to server")
                return

            recv_packet = self.recv_packet(BUFFER)

            if len(recv_packet) == 0:
                self.poutput("Err : Nothing received from the server")
                return
            
            unpacked_msg = Message.deserialize(recv_packet)

            if unpacked_msg[0] == MessageTypes.RESP_ERROR:
                self.poutput(unpacked_msg[1])

            self.poutput(DotTrail.print_level(unpacked_msg[1]))


        except OSError as e:
            self.poutput(e.with_traceback(e.__traceback__))
    
    def do_move(self, arg):
        if not self.socket:
            self.poutput("Register before utilizing other commands")
            return
        
        try:
            packed_msg = Message(MessageTypes.REQ_MOVE, arg).serialize()

            if not self.send_packet(packed_msg):
                self.poutput("Err : Failure to send msg to server")
                return

            recv_packet = self.recv_packet(BUFFER)

            if len(recv_packet) == 0:
                self.poutput("Err : Nothing received from the server")
                return
            
            unpacked_msg = Message.deserialize(recv_packet)

            if unpacked_msg[0] == MessageTypes.RESP_ERROR:
                self.poutput(unpacked_msg[1])

            self.poutput(DotTrail.print_level(unpacked_msg[1]))
        
        except OSError as e:
            self.poutput(e.with_traceback(e.__traceback__))

    def do_load(self, arg):
        pass

    def do_save(self, arg):
        pass

    @staticmethod
    def validate_registration(argument : str) -> tuple:

        regex_val = r'([A-Za-z0-9]+)@([A-Za-z0-9\.-]+):([0-9]{1,5})$'

        if not (match := re.search(regex_val, argument)):
            return None, None, None

        username = match.group(1)
        ip = match.group(2)
        port = match.group(3)

        if len(username) > 125:
            return None, None, None

        parts = ip.split(".")

        if len(parts) == 4:

            for i in parts:
                if not i.isdigit():
                    return None, None, None
                if int(i) not in range(0,256):
                    return None, None, None
                
        if int(port) < 1 or int(port) > 65535:

            return None, None, None
        
        return username, ip, port

    # def do_test(self,_):

    #     x = b'\x02\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x01\x00'

    #     print(DotTrail.print_level(x))

    @staticmethod  
    def print_level(level_bytes : bytes) -> str:
        level_bytes = bytearray(level_bytes)

        level_str = ""

        for i in range(len(level_bytes)):

            if i % 9 == 0 and i % 99 != 0:
                level_str += '-\n'           
            if level_bytes[i] == 1:
                level_str += '- '
            elif level_bytes[i] == 2:
                level_str += '* '
        
        return level_str
        

            


    def send_packet(self, packet) -> bool:
        
        if not self.socket:
            return False
        
        try:
            bytes_sent = 0

            self.socket.settimeout(2)

            while bytes_sent < len(packet):

                sent = self.socket.send(packet[bytes_sent:])
                if sent <= 0:
                    raise RuntimeError("Socket Connection broken")
                bytes_sent += sent
            
            self.poutput(f"Bytes Sent : {sent}")
            return True
        
        except (OSError, RuntimeError) as e:

            self.poutput(e)
            return False


    def recv_packet(self, size : int) -> bytes:
        
        if not self.socket:
            return b''
        try:
            bytes_recv = bytearray()
            self.socket.settimeout(2)

            while len(bytes_recv) <= size:
                recv = self.socket.recv(size - len(bytes_recv))
                if not recv:
                    raise RuntimeError("Connection Closed")
                bytes_recv.extend(recv)
            
            return bytes(bytes_recv)

        except (OSError, RuntimeError) as e:
            
            if (isinstance(e, RuntimeError)):
                self.poutput(e)
            
            elif isinstance(e, OSError):
                return bytes(bytes_recv)


