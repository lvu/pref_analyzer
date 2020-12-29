import json
import os
import sys

from os import path

sys.path.append(path.abspath('./src/main/python'))

from pref.analyze import Analyzer
from pref.ui import load_position, print_result

if __name__ == '__main__':
    data = json.load(sys.stdin)
    analyzer = Analyzer(data.get('trump'), data.get('misere', False))
    pos = load_position(data)
    result = analyzer.analyze_position(pos)
    print_result(pos, result)
