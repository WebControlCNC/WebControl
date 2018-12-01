from socketserver import ThreadingMixIn
import cv2
import http
from http.server import BaseHTTPRequestHandler, HTTPServer
import time

class CamHandler(BaseHTTPRequestHandler):

    def __init__(self, request, client_address, server):
        img_src = 'http://{}:{}/cam.mjpg'.format(server.server_address[0],
                                                 server.server_address[1])
        self.html_page = """
            <html>
                <head></head>
                <body>
                    <img src="{}"/>
                </body>
            </html>""".format(img_src)
        self.html_404_page = """
            <html>
                <head></head>
                <body>
                    <h1>NOT FOUND</h1>
                </body>
            </html>"""
        BaseHTTPRequestHandler.__init__(self, request, client_address, server)

    def do_GET(self):
        if self.path.endswith('.mjpg'):
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type',
                             'multipart/x-mixed-replace; boundary=--jpgboundary')
            self.end_headers()
            while True:
                try:
                    img = cam_reader.read_frame()
                    retval, jpg = cv2.imencode('.jpg', img)
                    if not retval:
                        raise RuntimeError('Could not encode img to JPEG')
                    jpg_bytes = jpg.tobytes()
                    self.wfile.write("--jpgboundary\r\n".encode())
                    self.send_header('Content-type', 'image/jpeg')
                    self.send_header('Content-length', len(jpg_bytes))
                    self.end_headers()
                    self.wfile.write(jpg_bytes)
                    time.sleep(cam_reader.read_delay)
                except (IOError, ConnectionError):
                    break
        elif self.path.endswith('.html'):
            self.send_response(http.HTTPStatus.OK)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_page.encode())
        else:
            self.send_response(http.HTTPStatus.NOT_FOUND)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(self.html_404_page.encode())


class ThreadedHTTPServer(ThreadingMixIn, HTTPServer):
    """Handle requests in a separate thread."""

    def __init__(self, server_address, RequestHandlerClass,
                 bind_and_activate=True):
        HTTPServer.__init__(self, server_address, RequestHandlerClass,
                            bind_and_activate)
        ThreadingMixIn.__init__(self)

    def serve_forever(self, poll_interval=0.5):
        super().serve_forever(poll_interval)
