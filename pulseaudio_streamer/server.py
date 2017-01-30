import logging
import socket
import threading
import errno

port_inc = 0

class Server:
    PORT_RANGE_START = 8804
    PORT_RANGE_END = 8854

    def __init__(self, stop_event,  encoder):
        self.encoder = encoder
        self.ip = socket.gethostbyname(socket.getfqdn())
        self.stop_streaming = threading.Event()
        self.thread = None
        self.stop_event = stop_event
        self.increment_port()

    def increment_port(self):
        global port_inc
        if self.PORT_RANGE_START + port_inc >= self.PORT_RANGE_END:
            port_inc = 0
        self.port = self.PORT_RANGE_START + port_inc
        port_inc += 1

    def start(self):
        self.thread = threading.Thread(target=self.serv)
        self.stop_streaming.clear()
        self.encoder.start()
        self.thread.start()

    def close_sock(self, sock):
        try:
            sock.shutdown(socket.SHUT_RDWR)
            sock.close()
        except OSError as err:
            if err.errno == errno.ENOTCONN: pass
            else: raise

    def serv(self):
        while True:
            try:
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(3)
                sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

                sock.bind(('', self.port))

                sock.listen(1)
                logging.debug('Socket listening on port: %i' % self.port)
                break
            except OSError as err:
                if err.errno == errno.EADDRINUSE:
                    self.increment_port()
                    pass
                else: raise

        try:
            conn, addr = sock.accept()
            logging.debug('Stream requested')

            request = conn.recv(1024)

            header = (b'HTTP/1.1 200 OK\r\n' +
                      b'Content-Type: audio/mp3\r\n' +
                      (b'Content-Length: %i\r\n' % (1024 * 1024 * 500)) +
                      b'Connection: Keep-Alive' +
                      b'\r\n')
            try:
                conn.send(header)
                while True:
                    if self.stop_streaming.wait(0): break
                    out = self.encoder.read()
                    if out: conn.send(out)
                    header = None
            except OSError as err:
                if err.errno == errno.ECONNRESET:
                    self.stop_event.set()
                else: raise

            logging.debug('Streaming stopped')
            self.close_sock(conn)
            self.close_sock(sock)


        except socket.timeout:
            logging.debug('Socket timeout')
            self.close_sock(sock)
        except:
            logging.debug('Closing socket')
            self.close_sock(sock)
            raise


    def stop(self):
        logging.debug('Stopping streaming')
        self.stop_streaming.set()
        self.encoder.stop()

        if self.thread != None and self.thread.isAlive():
            logging.debug('\t- Joining server thread')
            self.thread.join()
            self.thread = None
