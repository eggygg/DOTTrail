#!/usr/bin/env python3

import argparse
import cmd2
import re
import select
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
        #All the registration info is passed in the format username@ip:port
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

    def do_display(self, _):
        """displays current board to user"""
        #displays the current board to the user
        if not self.register_ran:
            self.poutput("Register before utilizing other commands")
            return
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
    
    move_parser = argparse.ArgumentParser()
    move_parser.add_argument("direction", choices=["up", "down", "left", "right"], help="Direction to move in")

    @cmd2.with_argparser(move_parser)
    def do_move(self, arg):
        """moves the player in the direction specified by the argument"""
        #arg should be one of the following : up, down, left, right
        if not self.register_ran:
            self.poutput("Register before utilizing other commands")
            return
        if not self.socket:
            self.poutput("Register before utilizing other commands")
            return
        
        try:
            packed_msg = Message(MessageTypes.REQ_MOVE, arg.direction).serialize()

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
        """Validates the registration argument and returns username, ip, port"""
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

    @staticmethod  
    def print_level(level_bytes : bytes) -> str:
        """Converts the level bytes to a string representation for display"""
        level_bytes = bytearray(level_bytes)

        level_str = ""

        for i in range(len(level_bytes)):

            if i % 9 == 0 and i % 99 != 0:
                level_str += '-\n'           
            if level_bytes[i] == 1:
                level_str += '- '
            elif level_bytes[i] == 2:
                level_str += '* '
            elif level_bytes[i] == 3:
                level_str += 'O '
        
        return level_str
        

            


    def send_packet(self, packet) -> bool:
        
        if not self.socket:
            return False
        
        try:
            bytes_sent = 0
            timeout = 5

            while bytes_sent < len(packet):
                ready = select.select([self.socket], [], [], timeout)
                if ready[0]:
                    sent = self.socket.send(packet[bytes_sent:])
                    if sent <= 0:
                        raise RuntimeError("Socket Connection broken")
                    bytes_sent += sent
                else:
                    break
            
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
            timeout = 5

            while len(bytes_recv) < size:
                ready = select.select([self.socket], [], [], timeout)
                if ready[0]:
                    recv = self.socket.recv(size - len(bytes_recv))
                    if not recv:
                        raise RuntimeError("Connection Closed")
                    bytes_recv.extend(recv)
                else:
                    break
            
            return bytes(bytes_recv)

        except (OSError, RuntimeError) as e:
            
            if (isinstance(e, RuntimeError)):
                self.poutput(e)
            
            elif isinstance(e, OSError):
                return bytes(bytes_recv)


