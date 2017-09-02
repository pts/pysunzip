#!/bin/sh
# by pts@fazekas.hu at Sat Sep  2 13:17:14 CEST 2017

""":" # sunzip.py: Streaming ZIP archive decompressor.

type python2.7 >/dev/null 2>&1 && exec python2.7 -- "$0" ${1+"$@"}
type python2.6 >/dev/null 2>&1 && exec python2.6 -- "$0" ${1+"$@"}
type python2.5 >/dev/null 2>&1 && exec python2.5 -- "$0" ${1+"$@"}
type python2.4 >/dev/null 2>&1 && exec python2.4 -- "$0" ${1+"$@"}
exec python -- ${1+"$@"}; exit 1

This is free software, GNU GPL >=2.0. There is NO WARRANTY. Use at your risk.

This script needs Python 2.4, 2.5, 2.6 or 2.7. Python 3.x won't work.

A similar tool (streaming unzip) implemented in C:
https://github.com/madler/sunzip/blob/master/sunzip.c
"""

import binascii
import struct
import sys


def main(argv):
  if len(argv) < 2:
    sys.exit('error: usage: %s <archive.zip> [<file> ...]' % argv[0])
  if argv[1] == '-':
    f, files = sys.stdin, argv[2:]
  else:
    f, files = open(argv[1], 'rb'), argv[2:]
  if files:
    print >>sys.stderr, 'info: extracting %d files from ZIP archive: %s' % (
       len(files), argv[1])
  else:
    print >>sys.stderr, 'extracting ZIP archive: %s' % argv[1]
  fc = 0
  data = f.read(4)
  # This loop is slow, but a fast and correct streaming version would be hard
  # to implement.
  while len(data) == 4 and data != 'PK\3\4':  # Skip junk at beginning.
    data = data[1:] + f.read(1)
  while 1:
    if data[:3] in ('PK\1', 'PK\5', 'PK\6'):
      while 1:
        data = f.read(65536)
        if not data:
          break
      break
    if data[:4] != 'PK\3\4': sys.exit('error: file header not found')
    data = f.read(26)
    _, _, mth, _, _, crc, cs, us, fnl, efl = struct.unpack('<HHHHHlLLHH', data)
    fn = f.read(fnl)  # filename looks like 'DIR1/DIR/FILE'.
    if len(fn) != fnl: sys.exit('error: EOF in filename')
    #print (mth, crc, cs, us, fnl, efl, fn)
    ef = f.read(efl)
    if len(ef) != efl: sys.exit('error: EOF in extra file data')
    if files and fn not in files:
      mth = -1  # Don't extract.
    else:
      fc += 1
      print >>sys.stderr, 'info: extracting file: %s (%d bytes)' % (fn, us)
      # 0: copy, 8: flate.
      if mth not in (0, 8):
        sys.exit('error: unknown method %d for file: %s' % (mth, fn))
      fn = fn.lstrip('/')  # Prevent writing to root.
      # Prevent writing to parent dirs.
      if '/../' in '/' + fn: sys.exit('error: insecure filename: %s' % file)
      if '/' in fn:
        try:
          __import__('os').makedirs(fn[:fn.rfind('/')])
        except OSError:
          pass
      uf = open(fn, 'wb')
    if mth == 8:
      zd = __import__('zlib').decompressobj(-15)
    i = c = s = 0
    while i < cs:
      j = min(65536, cs - i)
      data = f.read(j)
      if len(data) != j: sys.exit('error: EOF in file')
      i += j
      if mth == 8:
        data = zd.decompress(data)
      if mth != -1:
        s, c = s + len(data), binascii.crc32(data, c)
        uf.write(data)
    if mth == 8:
      data = zd.flush()
      s, c = s + len(data), binascii.crc32(data, c)
      uf.write(data)
    if mth != -1:
      uf.close()
      if s != us: sys.exit('error: size mismatch for file: ' + fn)
      if c != crc: sys.exit('CRC-32 mismatch for file: ' + fn)
    data = f.read(4)
  print >>sys.stderr, 'info: extracted %d files' % fc


if __name__ == '__main__':
  sys.exit(main(sys.argv))
