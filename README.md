# pyttygif

## (yet another) ttyrec to gif converter, written in Python

Create (optimized) animated GIFs of your terminal sessions by playing ttyrec file and screenshotting the terminal emulator.

ttyrec is a tool (and eponymous format) that's used to record a tty output and allow it to be played back later. Perhaps, one of most popular uses of it is to record roguelike game sessions (e.g. NetHack) to be played back later. In most Linux distros, it could be easily installed from repos.

pyttygif was developed with several goals in mind:

* Speed. While most ttyrec-to-GIF converters are either very slow or have a long post-processing stage, pyttygif is rather quick. It delegates most heavy work to the fast commandline tools (such as convert and gifsicle) and uses multiprocessing to parallelize the work.
* Modest memory usage. pyttygif doesn't load tons of huge, uncompressed bitmaps into the RAM (at least, not by default). It also doesn't create huge multi-gigabyte temporary directories. Resulting GIFs are also optimized and don't take a lot of disk space.
* Accuracy. Because it screenshots the running terminal - you can precisely control the appearance of output GIF by configuring your terminal emulator appearance. Also, pyttygif merges too short ttyrec frames, so that resulting GIF looks natural.
* Flexible. pyttygif already comes with sane defaults, but if you want to adjust something - there's a variety of advanced options. You could adjust GIF optimization level, or trade-off more RAM to reduce the processing time.
* Few dependencies. pyttygif is implemented in pure-python and should work on any Linux system with X11 and Python 3. For image processing, it depends on tools, such as xwd, convert (from imagemagick) and gifsicle, which are available in repos of most mainstream distros.

Warning: it's not recommended to move, resize, minimize, overlap with another window or otherwise interact with terminal emulator during the recording of GIF. It could cause artifacts, capturing portions of the overlapped windows and other undesired effects on the resulting GIF image. Or (if the window was minimized), it could fail the conversion outright.

## Usage

First, ensure that all required dependencies are installed. That is, x11-apps, imagemagick, and gifsicle.

For example, in Debian/Ubuntu, following should work:

> sudo apt-get install x11-apps imagemagick gifsicle

And in RedHat-based distros, following should do:

> sudo yum install xorg-x11-apps ImageMagick gifsicle

If any of the required tools are missing, pyttygif will inform you of that.
