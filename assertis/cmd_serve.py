import os
import sys
from pathlib import Path

import click

from assertis.comparison import write_comparison


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def serve(expected, actual, sensitivity):
    "Serve a web interface to view the comparison report."
    import http.server
    import socketserver
    import tempfile
    import threading
    import time

    from watchdog.events import FileSystemEventHandler
    from watchdog.observers import Observer

    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, expected, actual, report, sensitivity):
            self.expected = expected
            self.actual = actual
            self.report = report
            self.sensitivity = sensitivity

        def on_any_event(self, event):
            write_comparison(self.expected, self.actual, self.report, self.sensitivity)

    with tempfile.TemporaryDirectory() as temp_output:
        report_dir = Path(temp_output)

        # Run initial comparison
        write_comparison(expected, actual, report_dir, sensitivity)

        handler = ChangeHandler(expected, actual, report_dir, sensitivity)
        observer = Observer()
        observer.schedule(handler, path=expected, recursive=True)
        observer.schedule(handler, path=actual, recursive=True)
        observer.start()

        os.chdir(report_dir)
        PORT = 8000
        Handler = http.server.SimpleHTTPRequestHandler
        httpd = socketserver.TCPServer(("", PORT), Handler)

        print(f"Serving at port {PORT}")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.server_close()
        observer.stop()
        observer.join()
