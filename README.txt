sunzip.py: Streaming ZIP archive decompressor
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
sunzip.py is a simple streaming decompressor for ZIP archives, implemented
in Python. Streaming means that it reads the ZIP archive sequentially,
so it doesn't need a seekable ZIP input. Simple means that most ZIP features
(such as restoring the last modification times, or Unicode filenames) are
not supported.

Usage:

  ./sunzip.py <archive.zip> [<file> ...]

Usage with streaming input on Unix:

  cat archive.zip | ./sunzip.py

A similar tool (streaming unzip) implemented in C:
https://github.com/madler/sunzip/blob/master/sunzip.c

sunzip.py needs Python 2.4, 2.5, 2.6 or 2.7. Python 3.x won't work.

__END__
