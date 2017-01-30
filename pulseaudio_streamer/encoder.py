import os
import subprocess
import errno
import logging
import time
import select
import time
import threading

class Encoder:
    def __init__(self, m):
        in_rate = 44100
        in_chan = 2
        in_format = 's16le'
        in_dev = '%s.monitor' % m['name']

        out_format = 'mp3'
        out_rate = '320k'

        self.stop_encoding = threading.Event()

        self.enc_out = '/tmp/%s.out' % m['name']
        self.stream_path = '/tmp/%s.stream' % m['name']

        self.stream_fd_in = None
        self.stream_fd_out = None

        self.enc_fd_out = None
        self.enc_fd_in = None
        self.polling = None

        self.enc_proc = None
        self.rec_proc = None

        self.prec_com = ['/usr/bin/parec',
                         ('--format=%s' % in_format),
                         ('--rate=%i' % in_rate),
                         '-d', ('%s' % in_dev)]

        self.ffmpeg_com = ['/usr/bin/ffmpeg', '-ac', ('%i' % in_chan),
                           '-ar', ('%i' % in_rate),
                           '-f', in_format,
                           '-i', '-',
                           '-b:a', out_rate,
                           '-f', out_format, '-']

        self.devnull = open(os.devnull, 'wb')

    def __del__(self): self.devnull.close()

    def create_fifo(self, f):
        try:
            os.mkfifo(f)
        except OSError as e:
            if e.errno == errno.EEXIST:
                logging.debug("Pulseaudio Fifo file '%s' already exists" % f)
            else: raise
        except: raise

    def start(self):
        logging.debug("Starting encoding")

        self.stop_encoding.clear()

        self.create_fifo(self.enc_out)
        self.create_fifo(self.stream_path)

        self.enc_fd_out = os.open(self.enc_out, os.O_RDONLY | os.O_NONBLOCK)
        self.enc_fd_in = os.open(self.enc_out, os.O_WRONLY | os.O_NONBLOCK)
        self.stream_fd_out = os.open(self.stream_path, os.O_RDONLY | os.O_NONBLOCK)
        self.enc_proc = subprocess.Popen(self.ffmpeg_com,
                                         stdin=self.stream_fd_out,
                                         stderr=self.devnull,
                                         stdout=self.enc_fd_in)

        self.stream_fd_in = os.open(self.stream_path, os.O_WRONLY | os.O_NONBLOCK)
        self.rec_proc = subprocess.Popen(self.prec_com,
                                         stderr=self.devnull,
                                         stdout=self.stream_fd_in)
        self.polling = select.epoll(1)
        self.polling.register(self.enc_fd_out, select.EPOLLIN)

    @staticmethod
    def stop_proc(proc):
        if proc: proc.terminate()

    @staticmethod
    def close_fd(fd):
        if fd: os.close(fd)

    def stop(self):
        logging.debug("Stopping encoding")

        self.stop_encoding.set()

        self.enc_proc = self.stop_proc(self.enc_proc)
        self.rec_proc = self.stop_proc(self.rec_proc)
        logging.debug('\t- Shutdown encoder proccesses')

        self.enc_fd_out = self.close_fd(self.enc_fd_out)
        logging.debug('\t- Closed encoder out')
        self.enc_fd_in = self.close_fd(self.enc_fd_in)
        logging.debug('\t- Closed encoder in')
        self.stream_fd_out = self.close_fd(self.stream_fd_out)
        logging.debug('\t- Stream encoder out')
        self.stream_fd_in = self.close_fd(self.stream_fd_in)
        logging.debug('\t- Stream encoder in')

        if self.polling:
            self.polling.close()
            self.polling = None

        try:
            os.remove(self.enc_out)
            os.remove(self.stream_path)
        except os.error as err:
            if err.errno == errno.ENOENT: pass
            else: raise

        logging.debug('\t- Removed pipes')
        logging.debug('Encoding stopped')

    def read(self):
        try:
            if self.polling: self.polling.poll(1)
            else: return None
            if self.enc_fd_out: return os.read(self.enc_fd_out, 1024 * 16)
            else: return None
        except os.error as err:
            if errno.EAGAIN == err.errno:
                return None
            else:
                logging.debug('Failed to read from encoder output: %s' % errno.errorcode[err.errno])
                raise
