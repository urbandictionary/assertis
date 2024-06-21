import os
import sys

import click

from assertis.cmd_compare import compare
from assertis.cmd_fix import fix
from assertis.cmd_serve import serve
from assertis.cmd_verify import verify


@click.group()
def assertis():
    "Main entry point for the assertis CLI."
    pass


assertis.add_command(compare)
assertis.add_command(serve)
assertis.add_command(fix)
assertis.add_command(verify)

if __name__ == "__main__":
    assertis()
