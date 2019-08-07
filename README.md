# pyttygif

## (yet another) ttyrec to gif converter, written in Python

Create (optimized) animated GIFs of your terminal sessions by playing ttyrec file and screenshotting the terminal emulator.

![pyttygif demo](https://github.com/tmp6154/pyttygif/blob/master/img/demo.gif?raw=true "pyttygif demo")

ttyrec is a tool (and eponymous format) that's used to record a tty output and allow it to be played back later. Perhaps, one of most popular uses of it is to record roguelike game sessions (e.g. NetHack) to be played back later. In most Linux distros, it could be easily installed from repos.

pyttygif was developed with several goals in mind:

* Speed. While most ttyrec-to-GIF converters are either very slow or have a long post-processing stage, pyttygif is rather quick. It delegates most heavy work to the fast commandline tools (such as convert and gifsicle) and uses multiprocessing to parallelize the work.
* Modest memory usage. pyttygif doesn't load tons of huge, uncompressed bitmaps into the RAM (at least, not by default). It also doesn't create huge multi-gigabyte temporary directories. Resulting GIFs are also optimized and don't take a lot of disk space.
* Accuracy. Because it screenshots the running terminal - you can precisely control the appearance of output GIF by configuring your terminal emulator appearance. Also, pyttygif merges too short ttyrec frames, so that resulting GIF looks natural.
* Flexible. pyttygif already comes with sane defaults, but if you want to adjust something - there's a variety of advanced options. You could adjust GIF optimization level, or trade-off more RAM to reduce the processing time.
* Few dependencies. pyttygif is implemented in pure-python and should work on any Linux system with X11 and Python 3. For image processing, it depends on tools, such as xwd, convert (from imagemagick) and gifsicle, which are available in repos of most mainstream distros.

Warning: it's not recommended to move, resize, minimize, overlap with another window or otherwise interact with terminal emulator during the recording of GIF. It could cause artifacts, capturing portions of the overlapped windows and other undesired effects on the resulting GIF image. Or (if the window was minimized), it could fail the conversion outright.

## Installation

First, ensure that all required dependencies are installed. That is, x11-apps, imagemagick, and gifsicle.

For example, in Debian/Ubuntu, following should work:

    sudo apt-get install x11-apps imagemagick gifsicle

And in RedHat-based distros, following should do:

    sudo yum install xorg-x11-apps ImageMagick gifsicle

If any of the required tools are missing, pyttygif will inform you of that.

Then, install pyttygif from pip:

    sudo pip3 install pyttygif

Finally, you can convert a ttyrec like that:

    python3 -m pyttygif sample.ttyrec ./sample.gif

## Usage

    usage: __main__.py [-h] [-s SPEED] [-l LOOP] [-L LASTFRAME] [-m]
                       [-o {0,1,2,3}] [-S] [-b MAX_BACKLOG] [-D] [-f FPS]
                       [-c DELAYCAP]
                       input output
    
    Convert ttyrec to GIF animation
    
    optional arguments:
      -h, --help            show this help message and exit
    
    Main options:
      input                 Path to the ttyrec file to convert
      output                Path to save the resulting GIF
      -s SPEED, --speed SPEED
                            Speed multiplier
      -l LOOP, --loop LOOP  Number of times to play the GIF (0 = infinity)
    
    Advanced options:
      -L LASTFRAME, --lastframe LASTFRAME
                            How long to display the last frame
      -m, --no-conserve-memory
                            Use more RAM for speedup
      -o {0,1,2,3}, --optimize-level {0,1,2,3}
                            Optimize the GIF (levels 0-3)
      -S, --no-disable-screensaver
                            Don't disable screensaver during record
      -b MAX_BACKLOG, --max-backlog MAX_BACKLOG
                            In-RAM image backlog size (0 = infinite)
      -D, --dirty           Don't clear screen before record
      -f FPS, --fps FPS     How many frames to screenshot per second
      -c DELAYCAP, --delaycap DELAYCAP
                            Cap the display time of single frame (in seconds)

For the most basic usage, you only need to specify the required positional arguments (input ttyrec file path and output GIF file path). You can also specify **-s** to pass (floating point) speed multiplier to speed up or slow down the output GIF and **-l** to specify number of times to play the GIF (0 = infinity).

There's also a number of advanced options available.

* ttyrec format doesn't define display time of the last frame. However, you can alter display time of the last frame of the GIF with **-L** option (floating point number). It defaults to 5 seconds.
* pyttygif defaults to try to reduce RAM usage. If you want to speed up the conversion though, you can try to use **-m** flag (tells gifsicle to keep frames in RAM) and **-b** option, which adjusts the maximum number of frames to queue in RAM and defaults to the number of logical cores in the machine. It's not recommended to set it to less than number of cores. You can also set it to 0 (unlimited), however this is also not recommended because if your machine is unable to process all frames in time - it could eat all available RAM with a sufficiently long ttyrec.
* gifsicle optimization level defaults to 2, however you can override it with **-o** option and set it within range of 0-3 (where 0 is no optimization at all, tends to create huge GIFs, and 3 is maximum, but possibly slower).
* pyttygif attempts to inhibit screensaver by default (so that you don't have to move mouse during recording of the GIF to prevent screenlocker). However, if you don't want that for some reason (or don't have xdg-screensaver installed) - you might want to override it with **-S** flag.
* pyttygif clears the screen before recording it. However, if you want previous terminal content to be captured, you can pass in **-D** flag.
* pyttygif doesn't have any way to sync to the terminal emulator (and it also wants to be as much terminal-agnostic as possible), so the only way around this problem is to sleep a fixed amount of time after each displayed frame to give the terminal emulator some time to render the contents. pyttygif defaults to the more or less safe value of 25 FPS (which is 0.04 seconds of sleep after each frame). However, depending on your machine, you might want to override this, for example, with 60 FPS. You can specify the FPS with **-f** option. But beware of setting this value too high - it's possible that pyttygif would actually capture the previous frame, which would cause stutters and frame skips in the output GIF.
* If there's an excessively long delays in the input ttyrec (such as when user goes away from keyboard) - it's possible to cap such delays by passing **-c** option and specifying a maximum time in seconds that frame can take (floating point number). If any frame exceeds specified time - it's forcibly capped at that time. It defaults to positive infinity, that is, no capping.

## License

![GPLv3](https://github.com/tmp6154/pyttygif/blob/master/img/gplv3.png?raw=true "GPLv3")
