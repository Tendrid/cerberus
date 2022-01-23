import sys
from cerberus.bot import Cerberus

def main():
    client = Cerberus()
    client.run(str(sys.argv[1]))
