import sys
import click
import os
from cmd_compare import compare
from cmd_serve import serve
from cmd_fix import fix


@click.group()
def assertis():
    pass


assertis.add_command(compare)
assertis.add_command(serve)
assertis.add_command(fix)

if __name__ == "__main__":
    assertis()
