import sys
import click
import os
from assertis.cmd_compare import compare
from assertis.cmd_serve import serve
from assertis.cmd_fix import fix


@click.group()
def assertis():
    pass


assertis.add_command(compare)
assertis.add_command(serve)
assertis.add_command(fix)

if __name__ == "__main__":
    assertis()
