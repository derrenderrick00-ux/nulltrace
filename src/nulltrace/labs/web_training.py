"""Explicit, loopback-only synthetic HTTP lab for Burp Community/manual HTTP analysis.

This is not a security sandbox and is not intended to be network-accessible.
Start only on user command; there are no real accounts, tokens or personal data.
The intentionally missing case authorization check is part of the lesson.
"""
from __future__ import annotations
from datetime import datetime, timezone
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit
import json
import os
import time

RECEIPT_MAX_AGE = 7 * 24 * 60 * 60
TRAINING_RECORDS = {
    'alpha': {'case': 'alpha', 'owner': 'analyst-a', 'finding': 'Gateway report under review', 'classification': 'synthetic'},
    'mirror': {'case': 'mirror', 'owner': 'analyst-b', 'finding': 'MIRROR-07 omitted from summary', 'classification': 'synthetic'},
}


def receipt_file() -> Path:
    base = Path(os.environ.get('NULLTRACE_SAVE_DIR',
             Path(os.environ.get('XDG_DATA_HOME', Path.home() / '.local/share')) / 'nulltrace')).expanduser()
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    return base / 'web_lab_receipt.json'


def receipt_status() -> tuple[bool,str]:
    path = receipt_file()
    if not path.is_file():
        return False, 'No manual HTTP lab receipt. Start python -m nulltrace --web-lab in another terminal.'
    try:
        data = json.loads(path.read_text(encoding='utf-8'))
        if data.get('schema_version') != 1 or data.get('case') != 'mirror' or data.get('review') != 'authorized':
            return False, 'Receipt does not match the synthetic training exercise.'
        age = time.time() - data['completed_at']
        if not isinstance(age, (int,float)) or not -60 <= age <= RECEIPT_MAX_AGE:
            return False, 'Receipt expired or has an invalid timestamp. Repeat the lab.'
    except (OSError,ValueError,TypeError,KeyError):
        return False, 'Receipt is malformed; repeat the manual lab.'
    return True, 'Loopback training request was received. Manual Burp usage is not independently verifiable.'


def _html() -> bytes:
    return ("""<!doctype html><html lang='en'><meta charset='utf-8'><title>NULLTRACE · Local Web Lab</title>
<style>body{font:16px system-ui;background:#0c1724;color:#e7f3fa;max-width:690px;margin:35px auto;padding:15px}code,pre{color:#5ddbd3}a{color:#5ddbd3}li{margin:14px 0}</style>
<h1>NULLTRACE · Behind the Browser</h1><p>Loopback-only synthetic training portal. No genuine data or user accounts.</p>
<ol><li>Open <a href='/training/case?case=alpha'>your case (alpha)</a> through the configured Burp browser/proxy.</li>
<li>Send the HTTP request to Repeater; change the <code>case</code> query parameter to <code>mirror</code>.</li>
<li>Add <code>X-Nulltrace-Review: authorized</code> to the request headers and send it.</li>
<li>Observe that the fictional mirror record is returned with no case-owner authorization: an intentional training flaw.</li>
<li>Return to NULLTRACE and choose RUN CONTROLLED WEB LAB again to verify local completion.</li></ol>
<p>Note: other HTTP clients can perform the same lab; the receipt verifies a local HTTP request, not which client sent it.</p>
</html>""").encode('utf-8')


def make_handler(receipt_path: Path):
    class Handler(BaseHTTPRequestHandler):
        server_version = 'NulltraceLocalTraining/1.0'
        def log_message(self, fmt, *args):
            # Avoid recording arbitrary URLs, request identifiers or header values.
            pass
        def do_GET(self):
            url = urlsplit(self.path)
            if url.path == '/':
                self.respond(200, _html(), 'text/html; charset=utf-8')
                return
            if url.path == '/training/case':
                key = parse_qs(url.query).get('case', ['alpha'])[0]
                if key not in TRAINING_RECORDS:
                    self.respond(404, b'{"error":"Unknown synthetic case"}', 'application/json')
                    return
                # DELIBERATELY INSECURE TRAINING CASE: no object-level authorization.
                payload = json.dumps(TRAINING_RECORDS[key], sort_keys=True).encode()
                if key == 'mirror' and self.headers.get('X-Nulltrace-Review') == 'authorized':
                    tmp = receipt_path.with_suffix('.tmp')
                    doc = {'schema_version': 1, 'case': 'mirror', 'review': 'authorized',
                           'completed_at': time.time()}
                    try:
                        tmp.write_text(json.dumps(doc), encoding='utf-8')
                        os.chmod(tmp, 0o600)
                        tmp.replace(receipt_path)
                    except OSError:
                        self.respond(500, b'{"error":"Could not save lab receipt"}', 'application/json')
                        return
                self.respond(200, payload, 'application/json')
                return
            self.respond(404, b'Not found', 'text/plain')
        def respond(self, status: int, payload: bytes, media: str):
            self.send_response(status)
            self.send_header('Content-Type', media)
            self.send_header('Content-Length', str(len(payload)))
            self.send_header('Cache-Control', 'no-store')
            self.send_header('X-Content-Type-Options', 'nosniff')
            self.end_headers()
            self.wfile.write(payload)
        def do_POST(self):
            self.respond(405, b'Method not allowed', 'text/plain')
    return Handler


def start_server(port: int = 0, receipt_path: Path | None = None) -> ThreadingHTTPServer:
    """Return a server; caller owns serve_forever() and server_close().

    Bind is hard-coded to loopback, port 0 chooses an ephemeral port.
    """
    if not isinstance(port, int) or not 0 <= port < 65536:
        raise ValueError('Invalid TCP port')
    path = receipt_path or receipt_file()
    path.parent.mkdir(parents=True, exist_ok=True)
    server = ThreadingHTTPServer(('127.0.0.1', port), make_handler(path))
    server.daemon_threads = True
    return server


def serve_cli() -> int:
    server = start_server()
    host, port = server.server_address
    print('NULLTRACE LOCAL WEB LAB — synthetic training data ONLY', flush=True)
    print(f'Open http://127.0.0.1:{port}/ in the configured Burp browser.', flush=True)
    print('For Burp Repeater, send GET /training/case?case=mirror with X-Nulltrace-Review: authorized', flush=True)
    print('Server stays on loopback. Press Ctrl+C to stop.', flush=True)
    try:
        server.serve_forever(poll_interval=0.2)
    except KeyboardInterrupt:
        print('\nStopped local training portal.', flush=True)
    finally:
        server.server_close()
    return 0
