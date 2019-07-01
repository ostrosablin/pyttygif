# pyttygif

(yet another) ttyrec to gif converter, written in Python

Create animated GIFs by playing ttyrec file and screenshotting the terminal emulator.

pyttygif was developed with several goals in mind:

* Speed. While most ttyrec-to-GIF converters are either very slow or have a long post-processing stage, pyttygif is rather quick. It delegates most heavy work to the fast commandline tools (such as convert and gifsicle) and uses threads to parallelize the work.
* Modest memory usage. pyttygif doesn't load tons of huge, uncompressed bitmaps into the RAM (at least, not by default). It also doesn't create huge multi-gigabyte temporary directories.
* Accurate. Because it screenshots the running terminal - you can precisely control the appearance of output gif by configuring your terminal emulator appearance. Also, pyttygif merges too short ttyrec frames, so that resulting GIF looks natural.
* Flexible. pyttygif already comes with sane defaults, but if you want to adjust something - there's a variety of advanced options. You could adjust GIF optimization level, or trade-off more RAM to reduce the processing time.
* Few dependencies. pyttygif is implemented in pure-python and should work on any Linux system with X11 and Python 3. For image processing, it depends on tools, such as xwd, convert (from imagemagick) and gifsicle, which are available in repos of most mainstream distros.
