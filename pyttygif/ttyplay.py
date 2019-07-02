#      This file is part of pyttygif.
#
#      pyttygif is free software: you can redistribute it and/or modify
#      it under the terms of the GNU General Public License as published by
#      the Free Software Foundation, either version 3 of the License, or
#      (at your option) any later version.
#
#      pyttygif is distributed in the hope that it will be useful,
#      but WITHOUT ANY WARRANTY; without even the implied warranty of
#      MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#      GNU General Public License for more details.
#
#      You should have received a copy of the GNU General Public License
#      along with pyttygif.  If not, see <https://www.gnu.org/licenses/>.

import struct
import io
import sys


class TtyPlay(object):
    """
    A class to read, analyze and play ttyrecs
    """
    def __init__(self, f, speed=1.0):
        """
        Create a new ttyrec player.

        :param f: An open file object or a path to file.
        :param speed: Speed multipier, used to divide delays.
        """
        if isinstance(f, io.IOBase):
            self.file = f
        else:
            self.file = open(f, 'rb')
        self.speed = speed  # Multiplier of speed
        self.seconds = 0  # sec field of header
        self.useconds = 0  # usec field of header
        self.length = 0  # len field of header
        self.frameno = 0  # Number of current frame in file
        self.duration = 0.0  # Computed duration of previous frame
        self.frame = bytes()  # Payload of the frame

    def compute_framelen(self, sec, usec):
        """
        Compute the length of previous frame.

        :param sec: Current frame sec field
        :param usec: Current frame usec field
        :return: Float duration of previous frame in seconds
        """
        secdiff = sec - self.seconds
        usecdiff = (usec / 1000000.0) - (self.useconds / 1000000.0)
        duration = (secdiff + usecdiff) / self.speed
        if duration < 0:
            raise ValueError("ttyrec frame is in past")
        return duration

    def compute_framedelays(self):
        """
        Walk through the ttyrec file and calculate lengths of all frames.

        :return: List, containing delays for each frame.
        """
        self.file.seek(0)
        delays = []
        while self.read_frame(loop=True):
            if self.frameno > 1:
                delays.append(self.duration)
        return delays

    def read_frame(self, loop=False):
        """
        Read a ttyrec frame (header and payload).

        :param loop: If True, rewind ttyrec after reaching EOF (don't close).
        :return: True, if there's more to read, False if reached EOF.
        """
        header = self.file.read(12)
        if len(header) == 0:
            if loop:
                self.file.seek(0)
                self.frameno = 0
            else:
                self.file.close()
            return False
        elif len(header) < 12:
            raise ValueError("Short read: Couldn't read a whole ttyrec header!")
        seconds, useconds, length = struct.unpack('<III', header)
        self.frame = self.file.read(length)
        if len(self.frame) < length:
            raise ValueError("Short read: Couldn't read a whole ttyrec frame!")
        self.frameno += 1
        if self.frameno > 1:
            self.duration = self.compute_framelen(seconds, useconds)
        self.seconds = seconds
        self.useconds = useconds
        self.length = length
        return True

    def display_frame(self):
        """
        Print the frame to stdout.

        :return: None
        """
        sys.stdout.write(str(self.frame, errors='ignore'))
        sys.stdout.flush()

    def close(self):
        """
        Close the ttyrec file object.

        :return: None
        """
        self.frame = None
        self.file.close()

    def __enter__(self):
        """
        Allows to use ttyrec player with context management.

        :return: Self
        """
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        """
        Allows to use ttyrec player with context management.

        :param exc_type: Exception type (if any).
        :param exc_val: Exception object (if any).
        :param exc_tb: Exception backtrace (if any).
        :return: None
        """
        self.file.close()
