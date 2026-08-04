# Serve the presentation with RANGE support.
#
# Python's http.server does not answer Range requests, and without them a
# browser cannot seek inside an audio file: the scrubber moves, the
# playhead does not. Twenty lines fixes it.
#
#   ./venv/Scripts/python.exe playtest_presentation/serve.py
#   ... --port 8088
#
# (Opening index.html straight from disk also works in a normal browser -
# this is only for a proper localhost with working seek.)

import argparse
import functools
import http.server
import os
import socketserver
import webbrowser
from pathlib import Path

HERE = Path(__file__).resolve().parent
# Served from the REPO ROOT, not from this folder: every slide links to
# real source files with paths like ../tools/playtest/battle_gauntlet.py,
# and those only resolve when the root is what is being served.
REPO_ROOT = HERE.parent


class RangeHandler(http.server.SimpleHTTPRequestHandler):
    """SimpleHTTPRequestHandler plus HTTP 206 partial responses"""

    def send_head(self):
        range_header = self.headers.get('Range')
        if not range_header or not range_header.startswith('bytes='):
            return super().send_head()

        path = self.translate_path(self.path)
        if os.path.isdir(path):
            return super().send_head()
        try:
            # Handed to copyfile, which closes it - the same ownership
            # SimpleHTTPRequestHandler.send_head uses
            handle = open(path, 'rb')  # noqa: SIM115
        except OSError:
            self.send_error(404, 'File not found')
            return None

        size = os.fstat(handle.fileno()).st_size
        first, _, last = range_header[6:].partition('-')
        start = int(first) if first else 0
        end = int(last) if last else size - 1
        end = min(end, size - 1)
        if start > end:
            handle.close()
            self.send_error(416, 'Requested range not satisfiable')
            return None

        handle.seek(start)
        self.send_response(206)
        self.send_header('Content-Type', self.guess_type(path))
        self.send_header('Content-Range', f'bytes {start}-{end}/{size}')
        self.send_header('Content-Length', str(end - start + 1))
        self.send_header('Accept-Ranges', 'bytes')
        self.end_headers()
        return _Bounded(handle, end - start + 1)

    def end_headers(self):
        self.send_header('Accept-Ranges', 'bytes')
        super().end_headers()

    def log_message(self, *args):
        pass  # a presentation does not need a request log


class _Bounded:
    """Reads at most `remaining` bytes - copyfile stops where we say"""

    def __init__(self, handle, remaining):
        self.handle = handle
        self.remaining = remaining

    def read(self, amount=-1):
        if self.remaining <= 0:
            return b''
        if amount < 0 or amount > self.remaining:
            amount = self.remaining
        chunk = self.handle.read(amount)
        self.remaining -= len(chunk)
        return chunk

    def close(self):
        self.handle.close()


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--port', type=int, default=8088)
    parser.add_argument('--no-browser', action='store_true')
    args = parser.parse_args()

    handler = functools.partial(RangeHandler, directory=str(REPO_ROOT))
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(('127.0.0.1', args.port), handler) as server:
        url = f'http://localhost:{args.port}/{HERE.name}/'
        print(f'Playtesting Without Playing -> {url}   (ctrl-c to stop)')
        if not args.no_browser:
            webbrowser.open(url)
        try:
            server.serve_forever()
        except KeyboardInterrupt:
            print('\nstopped')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
