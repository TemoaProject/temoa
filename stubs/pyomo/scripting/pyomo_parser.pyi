import argparse

from _typeshed import Incomplete

class CustomHelpFormatter(argparse.RawDescriptionHelpFormatter): ...

def get_version(): ...

doc: str
epilog: str
subparsers: Incomplete

def add_subparser(name, **args): ...
def get_parser(): ...
