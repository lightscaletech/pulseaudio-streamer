import os
import subprocess
import errno
import logging
import time
from select import select


class Encoder:
    def __init__(self, m):
        in_rate = 44100
        in_chan = 2
        in_format = 's16le'
        in_dev = '%s.monitor' % m['name']

        out_format = 'mp3'
        out_rate = '320k'

        self.enc_out = '/tmp/%s.out' % m['name']

        prec_com = ('parec --format=%s --rate=%i -d %s | ' %
                    (in_format, in_rate, in_dev))

        ffmpeg_com = (('ffmpeg -ac %i ' % in_chan) +
                      ('-ar %i ' % in_rate) +
                      ('-f %s ' % in_format) +
                      '-i - ' +
                      ('-b:a %s ' % out_rate) +
                      ('-f %s ' % out_format) +
                      ('- > %s' % self.enc_out))

        self.command = prec_com + ffmpeg_com

        self.devnull = open(os.devnull, 'wb')

    def __del__(self): self.devnull.close()

    def create_fifo(self, f):
        try:
            os.mkfifo(f)
        except OSError as e:
            if e.errno == errno.EEXIST:
                logging.debug("Pulseaudio Fifo file '%s' already exists" % f)

    def start(self):
        logging.debug("Starting encoding")
        self.create_fifo(self.enc_out)
        self.enc_proc = subprocess.Popen(self.command, shell=True,
                                        stderr=self.devnull, stdout=self.devnull)
        self.enc_fd = open(self.enc_out, 'rb')

    def stop(self):
        logging.debug("Stopping encoding")
        self.enc_proc.kill()
        self.enc_fd.close()
        os.remove(self.enc_out)

    def read(self):
        return self.enc_fd.read(1024 * 8)

