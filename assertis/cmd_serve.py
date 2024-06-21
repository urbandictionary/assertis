import sys
import click
import os
from assertis.comparison import run_comparison
from pathlib import Path


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
    import threading
    import time
    import tempfile
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, expected, actual, output, sensitivity):
            self.expected = expected
            self.actual = actual
            self.output = output
            self.sensitivity = sensitivity

        def on_any_event(self, event):
            run_comparison(self.expected, self.actual, self.output, self.sensitivity)

    with tempfile.TemporaryDirectory() as temp_output:
        output_dir = Path(temp_output)

        # Run initial comparison
        run_comparison(expected, actual, output_dir, sensitivity)

        handler = ChangeHandler(expected, actual, output_dir, sensitivity)
        observer = Observer()
        observer.schedule(handler, path=expected, recursive=True)
        observer.schedule(handler, path=actual, recursive=True)
        observer.start()

        os.chdir(output_dir)
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
