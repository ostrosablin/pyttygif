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

import argparse
import os
import sys
import time
import shutil
import subprocess
import multiprocessing
import datetime

from pyttygif import ttyplay, capture, gifbuilder

# CLI tools that we absolutely depend on
DEPENDS_ON = ['xwd', 'convert', 'clear', 'stty', 'reset', 'gifsicle']


def toggle_screensaver(win_id, enable=False):
    """
    Set the desired screensaver state.

    :param win_id: Window ID to request from.
    :param enable: Enable screensaver if True, else disable.
    :return: None.
    """
    cmd = ['xdg-screensaver', 'resume' if enable else 'suspend', win_id]
    subprocess.check_call(cmd)


def clear_screen():
    """
    Clear and reset screen and set sane settings.

    :return: None.
    """
    cmds = (('clear',), ('reset',), ('stty', 'sane'))
    for cmd in cmds:
        subprocess.check_call(cmd)


def gif_frames_worker(taskqueue, resultqueue, nextqueue):
    """
    Worker for converting GIF frames.

    :return: None.
    """
    while True:
        task = taskqueue.get()
        if task is None:
            return
        frmno, img = task
        try:
            frame = capture.convertimage(img)
        except (SystemError, BrokenPipeError):
            resultqueue.put(sys.exc_info())
            return
        nextqueue.put((frmno, frame))  # Push prepared frame to build final GIF
        taskqueue.task_done()


def gif_build_worker(taskqueue, resultqueue, gifbldr):
    """
    Worker for building final GIF.

    :return: None.
    """
    curfrm = 1
    pending = {}
    while True:
        task = taskqueue.get()
        if task is None:
            return
        frmno, frame = task
        try:
            if frmno == curfrm:
                gifbldr.add_image(frame)
                curfrm += 1
            else:
                pending[frmno] = frame
            if pending:
                while curfrm in pending:
                    gifbldr.add_image(pending.pop(curfrm))
                    curfrm += 1
        except (SystemError, BrokenPipeError):
            resultqueue.put(sys.exc_info())
            return
        taskqueue.task_done()


# Arg parsing and initial handling
args = None

parser = argparse.ArgumentParser(description='Convert ttyrec to GIF animation')
maingroup = parser.add_argument_group("Main options")
maingroup.add_argument('input', default=None,
                       help="Path to the ttyrec file to convert")
maingroup.add_argument('output', default=None,
                       help="Path to save the resulting GIF")
maingroup.add_argument('-s', '--speed', default=1.0,
                       type=float, help="Speed multiplier")
maingroup.add_argument('-l', '--loop', default=1, type=int,
                       help="Number of times to play the GIF (0 = infinity)")

advgroup = parser.add_argument_group("Advanced options")
advgroup.add_argument('-L', '--lastframe', default=5.0, type=float,
                      help="How long to display the last frame")
advgroup.add_argument('-m', '--no-conserve-memory', default=False,
                      action='store_true', help="Use more RAM for speedup")
advgroup.add_argument('-o', '--optimize-level', default=2, choices=range(0, 4),
                      type=int, help="Optimize the GIF (levels 0-3)")
advgroup.add_argument('-S', '--no-disable-screensaver', default=False,
                      action='store_true',
                      help="Don't disable screensaver during record")
advgroup.add_argument('-b', '--max-backlog',
                      default=multiprocessing.cpu_count(), type=int,
                      help="In-RAM image backlog size (0 = infinite)")
advgroup.add_argument('-D', '--dirty', default=False, action='store_true',
                      help="Don't clear screen before record")

try:
    args = parser.parse_args()
except argparse.ArgumentError:
    parser.print_help()
    sys.exit(0)

if not args.input:
    print("Input ttyrec file omitted, nothing to do.")
    sys.exit(1)
if not args.output:
    print("Output file not specified, nothing to do.")
    sys.exit(1)
if not args.no_disable_screensaver:
    DEPENDS_ON.append("xdg-screensaver")

# Get WINDOWID for taking screenshots of terminal
windowid = os.getenv('WINDOWID')
if not windowid:
    print("Couldn't get WINDOWID environment variable, quitting...")
    sys.exit(1)
try:
    int(windowid)
except ValueError:
    print("WINDOWID environment variable should be an integer")
    sys.exit(1)

# Check that all required CLI tools are present
for util in DEPENDS_ON:
    if not shutil.which(util):
        print("Required utility missing: {0}".format(util))
        sys.exit(1)

time_start = time.time()
tp = ttyplay.TtyPlay(args.input, args.speed)  # Create a tty player
# Here we do a two-pass run over ttyrec. On 1st pass we get frame
# lengths from ttyrec and calculate delays for GIF frames.
delays = tp.compute_framedelays()
delays.append(args.lastframe)  # To allow last iteration to pass
in_frames = len(delays)

# Next is a little optimization. Ttyrec frames are in microsecond
# resolution and could be very small. So, we join several very short
# frames into a single GIF frame with reasonable timing.
gifdelays = []
vislength = 0.0

for delay in delays:
    vislength += delay
    if vislength <= 0.01:
        continue
    gifdelays.append(vislength)
    vislength = 0.0

# Make a GIF builder with pre-computed frame delays.
gif = gifbuilder.GifBuilder(args.output, gifdelays, args.loop,
                            args.optimize_level,
                            not args.no_conserve_memory)

# Clear screen before playback. The idea is to clear pyttygif invocation.
if not args.dirty:
    clear_screen()

# Prepare for the main loop (second pass over the ttyrec).
vislength = 0.0
gifframe = 1  # GIF frame counter is used to reorder frames back.

# We use worker processes to convert frames and build GIF for speedup.
framequeue = multiprocessing.JoinableQueue(args.max_backlog)
# This queue is used to report exceptions from workers
errorqueue = multiprocessing.JoinableQueue()
# This queue is used to pass converted frames to GIF builder.
gifqueue = multiprocessing.JoinableQueue(args.max_backlog)
workers = []
for i in range(multiprocessing.cpu_count()):
    p = multiprocessing.Process(target=gif_frames_worker,
                                args=(framequeue, errorqueue, gifqueue))
    p.daemon = True
    p.start()
    workers.append(p)

builder = multiprocessing.Process(target=gif_build_worker,
                                  args=(gifqueue, errorqueue, gif))
builder.start()

if not args.no_disable_screensaver:  # Inhibit screen lock
    toggle_screensaver(windowid)

# Main recording loop.
try:
    while tp.read_frame():
        tp.display_frame()
        vislength += delays[tp.frameno - 1]
        if vislength <= 0.01:  # GIF counts delays in hundredths of seconds
            continue  # We discard frames that are less than this.
        else:
            vislength = 0.0
        # Let the terminal emulator draw the frame. Without this it's possible
        # to capture partial draws. It's not a strict guarantee, but seems to
        # work reasonably well.
        time.sleep(0.01)
        # Capture the image of terminal and queue it for GIF convert
        image = capture.capturewithretry(windowid)
        framequeue.put((gifframe, image), True, 1)
        if not errorqueue.empty():
            exc_info = errorqueue.get()
            raise exc_info[1].with_traceback(exc_info[2])
        gifframe += 1
except (ValueError, SystemError, BrokenPipeError) as e:
    clear_screen()
    print("Main processing loop failed:")
    print("{0}: {1}".format(type(e).__name__, e))
    sys.exit(1)
except KeyboardInterrupt:
    time.sleep(0.1)
    clear_screen()
    print("User has cancelled rendering")
    sys.exit(1)

if not args.no_disable_screensaver:  # Reenable screen lock
    toggle_screensaver(windowid, True)

# Finish processing and stop worker processes.
framequeue.join()
for p in workers:
    p.terminate()

gifqueue.join()
builder.terminate()

# Close the GifBuilder to write the GIF to disk.
gif.close()

# Close ttyrec file.
tp.close()

# Print stats and quit:
clear_screen()
time_end = time.time()
out_frames = len(gifdelays)
giflength = sum(filter(lambda x: round(x * 100) / 100, gifdelays))
print("Stats:\n")
print("Rendered GIF in {0}".format(
    str(datetime.timedelta(seconds=time_end-time_start))))
print("ttyrec duration: {0}".format(
    str(datetime.timedelta(seconds=sum(delays[:-1])))))
print("GIF duration: {0}".format(
    str(datetime.timedelta(seconds=giflength))))
print("Input frames from ttyrec: {0}".format(in_frames))
print("Output frames in GIF: {0}".format(out_frames))
print("Dropped frames: {0}\n".format(in_frames - out_frames))
print("Done!")