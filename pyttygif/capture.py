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


def capturewithretry(windowid, retries=5):
    """
    Wrapper for capturewindow. xwd sometimes seems to fail randomly. In that
    case, retry the screenshot capture.

    :param windowid: Window ID of the window to capture.
    :param retries: Number of times to retry capture.
    :return: Raw image bytes.
    """
    while True:
        try:
            return capturewindow(windowid)
        except ChildProcessError:
            retries -= 1
            if retries == 0:
                raise


def capturewindow(windowid):
    """
    Capture an uncompressed XWD image (X Window Dump) of the window.

    :param windowid: Window ID of the window to capture.
    :return: Raw image bytes.
    """
    capcmd = ['xwd', '-silent', '-id', windowid]
    cap = subprocess.Popen(capcmd, stdout=subprocess.PIPE,
                           stderr=subprocess.PIPE, bufsize=-1)
    image = cap.communicate()[0]
    if cap.wait():
        raise ChildProcessError("Failed to capture the window: {0}"
                                .format(cap.returncode))
    return image


def convertimage(image):
    """
    Convert XWD image into a still GIF frame.

    :param image: Raw XWD image bytes.
    :return: Compressed GIF image.
    """
    convcmd = ['convert', 'xwd:-', 'gif:-']
    conv = subprocess.Popen(convcmd, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            bufsize=-1)
    newimage = conv.communicate(image)[0]
    if conv.wait():
        raise ChildProcessError("Failed to convert the image: {0}"
                                .format(conv.returncode))
    return newimage
