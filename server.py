from BaseHTTPServer import BaseHTTPRequestHandler,HTTPServer

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        print("get request")
        f = open("/home/sam/Music/Mailman/No News Is Good News/01 Dream About Love.mp3", 'rb')
        data = f.read()
        length = len(data)
        self.send_response(200)
        self.send_header('Content-Type', 'audio/mpeg')
        self.send_header('Content-Length', length)
        self.end_headers()
        self.wfile.write(data)
        return

class Server:
    PORT = 8804

    def start(self):
        self.server = HTTPServer(('', self.PORT), Handler)

    def stop(self):
        self.server.server_close()

    def wait(self):
        self.server.serve_forever()
