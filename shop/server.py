import socketserver
import pickle

class DeltaHandler(socketserver.BaseRequestHandler):
    def handle(self):
        self.data = ''
        while w := self.request.recv(1024).strip(): self.data += w
        try:
            print(pickle.loads(self.data))
        except pickle.UnpicklingError:
            self.request.sendall(b'FAIL')
        else:
            self.request.sendall(b'SUCCESS')
