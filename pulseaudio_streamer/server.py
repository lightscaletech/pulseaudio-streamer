import logging
import socket
import threading

port_inc = 0

class Server:
    START_PORT = 8804

    def __init__(self, encoder):
        self.encoder = encoder
        self.ip = socket.gethostbyname(socket.getfqdn())
        self.stop_streaming = threading.Event()
        self.thread = None
        global port_inc
        self.port = self.START_PORT + port_inc
        port_inc += 1

    def start(self):
        self.thread = threading.Thread(target=self.serv)
        self.stop_streaming.clear()
        self.encoder.start()
        self.thread.start()

    def close_sock(self, sock):
        logging.debug("closing socket")
        sock.shutdown(socket.SHUT_RDWR)
        sock.close()


    def serv(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        sock.bind(('', self.port))

        sock.listen(1)
        logging.debug('Socket listening on port: %i' % self.port)

        try:
            conn, addr = sock.accept()
            logging.debug('Stream requested')

            request = conn.recv(1024)

            header = ('HTTP/1.1 200 OK\r\n' +
                      'Content-Type: audio/mp3\r\n' +
                      ('Content-Length: %i\r\n' % (1024 * 1024 * 100)) +
                      'Connection: Keep-Alive' +
                      '\r\n')

            while True:
                if self.stop_streaming.wait(0): break
                out = self.encoder.read()
                conn.send(header + out)
                header = ''

            logging.debug('Streaming stopped')
            conn.shutdown(socket.SHUT_RDWR)
            conn.close()
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
