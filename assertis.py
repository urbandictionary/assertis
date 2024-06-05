import sys
import click
from comparison import run_comparison
from pathlib import Path


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--output",
    prompt="Output directory",
    help="Directory to store the output report and images.",
)
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def compare(expected, actual, output, sensitivity):
    output_dir = Path(output)
    if output_dir.exists() and any(output_dir.iterdir()):
        print(
            "Output directory already exists and is not empty. Please remove it first."
        )
        sys.exit(1)

    has_changes = run_comparison(expected, actual, output_dir, sensitivity)
    if has_changes:
        sys.exit(1)
    else:
        sys.exit(0)


@click.command()
@click.argument("expected")
@click.argument("actual")
@click.option(
    "--sensitivity",
    default=0,
    help="Sensitivity level for detecting changes (0-100, default is 0).",
)
def serve(expected, actual, sensitivity):
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


@click.group()
def assertis():
    pass


assertis.add_command(compare)
assertis.add_command(serve)

if __name__ == "__main__":
    assertis()
