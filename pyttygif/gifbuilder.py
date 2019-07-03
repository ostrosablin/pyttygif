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

import subprocess


class GifBuilder(object):
    """
    Wrapper around gifsicle CLI utility.
    """
    def __init__(self, path, delays, loop=1, optimize=3, conserve_memory=True):
        """
        Spawn a new gifsicle process.

        :param path: Path of GIF to create.
        :param delays: A list of delays for each frame.
        :param loop: Number of repeats for GIF (0 - infinity).
        :param optimize: Optimization level of GIF (0-3).
        :param conserve_memory: Whether to save RAM at cost of processing time.
        """
        cmd = ['gifsicle', '--nextfile', '--no-comments',
               '--{0}conserve-memory'.format('' if conserve_memory else 'no-')]
        if loop <= 0:
            cmd.append('--loopcount')
        elif loop == 1:
            cmd.append('--no-loopcount')
        else:
            cmd.append('--loopcount={0}'.format(str(loop-1)))
        if optimize:
            cmd.append('-O{0}'.format(str(optimize)))
            cmd.append('-Okeep-empty')
        for delay in delays:
            cmd.append('-d{0}'.format(str(GifBuilder.gifdelay(delay))))
            cmd.append('-')
        cmd.append('-o')
        cmd.append(path)
        cmd.append('--done')
        self.cmd = cmd
        self.gifsicle = None
        self.closed = False

    @staticmethod
    def gifdelay(s):
        """
        Convert float seconds into integer hundredths of seconds.

        :param s: Float, representing the delay.
        :return: Integer, representing the delay in GIF format.
        """
        return round(s * 100)

    def start(self):
        """
        Start the gifsicle process.

        :return: None.
        """
        try:
            self.gifsicle = subprocess.Popen(self.cmd, stdin=subprocess.PIPE,
                                             stdout=subprocess.PIPE,
                                             stderr=subprocess.PIPE,
                                             bufsize=-1)
        except FileNotFoundError:
            raise ChildProcessError("Gifsicle doesn't seem to be installed")

    def add_image(self, image):
        """
        Add a still GIF image to the resulting animated GIF.

        :param image: Bytes, representing the GIF image frame.
        :return: None.
        """
        if self.closed:
            raise ChildProcessError("Write to closed GifBuilder")
        if self.gifsicle is None:
            raise ChildProcessError("Gifsicle process is not started yet")
        try:
            self.gifsicle.stdin.write(image)
        except BrokenPipeError as e:
            self.terminate()
            ret = self.gifsicle.wait()
            self.gifsicle = None
            if ret is not None:
                raise ChildProcessError("Gifsicle exited unexpectedly "
                                        "with code {0}".format(ret)) from e

    def terminate(self):
        """
        Terminate the gifsicle process non-gracefully.

        :return: None.
        """
        if self.gifsicle is None:
            return
        self.gifsicle.terminate()
        self.gifsicle.poll()
        self.closed = True

    def close(self):
        """
        Close the stdin and write GIF to the disk.

        :return: None.
        """
        if self.gifsicle is None:
            return
        self.gifsicle.stdin.close()
        self.closed = True
        ret = self.gifsicle.wait()
        if ret:
            raise ChildProcessError("Failed to build GIF: {0}"
                                    .format(ret))

    def __enter__(self):
        """
        Allows to use GIF builder with context management.

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
        self.close()
