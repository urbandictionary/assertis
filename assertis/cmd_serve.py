import http.server
import os
import sys
import tempfile
import threading
import time
from pathlib import Path

import click
from watchdog.events import FileSystemEventHandler
from watchdog.observers import Observer

from assertis.comparison import write_comparison


def write_comparison_with_timing(expected, actual, report_dir, sensitivity):
    click.echo("Writing comparison...")
    start_time = time.time()
    write_comparison(expected, actual, report_dir, sensitivity)
    end_time = time.time()
    duration = end_time - start_time
    click.echo(f"Comparison written in {duration:.2f} seconds.")


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
@click.option(
    "--port",
    default=8000,
    help="Port to run the server on (default is 8000).",
)
def serve(expected, actual, sensitivity, port):
    "Serve a web interface to view the comparison report."

    class ChangeHandler(FileSystemEventHandler):
        def __init__(self, expected, actual, report, sensitivity):
            self.expected = expected
            self.actual = actual
            self.report = report
            self.sensitivity = sensitivity

        def on_any_event(self, event):
            if event.event_type in ['created', 'deleted', 'modified', 'moved'] and not event.is_directory:
                click.echo(f"Event detected: {event.event_type} on file {event.src_path}")
                write_comparison_with_timing(
                    self.expected, self.actual, self.report, self.sensitivity
                )

    with tempfile.TemporaryDirectory() as temp_output:
        report_dir = Path(temp_output)

        # Run initial comparison
        write_comparison_with_timing(expected, actual, report_dir, sensitivity)

        handler = ChangeHandler(expected, actual, report_dir, sensitivity)
        observer = Observer()
        observer.schedule(handler, path=expected, recursive=True)
        observer.schedule(handler, path=actual, recursive=True)
        observer.start()

        class CustomHandler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory=str(report_dir), **kwargs)

            def do_GET(self):
                if self.path == "/run":
                    write_comparison_with_timing(
                        expected, actual, report_dir, sensitivity
                    )
                    self.send_response(302)
                    self.send_header("Location", "/")
                    self.end_headers()
                else:
                    super().do_GET()

        httpd = http.server.ThreadingHTTPServer(("", port), CustomHandler)

        click.echo(f"Serving report from {report_dir} at http://localhost:{port}")
        click.echo(f"Visit http://localhost:{port}/run to force a comparison update")
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            pass
        httpd.shutdown()
        httpd.server_close()
        observer.stop()
        observer.join()
