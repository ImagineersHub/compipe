import glob
from os.path import basename, dirname, sep
modules = glob.glob(f"{dirname(__file__)}{sep}cmd_*.py")
__all__ = [basename(cmd)[:-3] for cmd in modules]
