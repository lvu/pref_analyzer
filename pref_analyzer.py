import json
import os
import sys

from os import path

sys.path.append(path.abspath('./src/main/python'))

from pref.cards import Suite
from pref.analyze import Analyzer
from pref.ui import load_position, print_result

if __name__ == '__main__':
    data = json.load(sys.stdin)
    trump_str = data.get('trump')
    trump = None if trump_str is None else Suite(trump_str)
    analyzer = Analyzer(trump, data.get('misere', False))
    pos = load_position(data)
    result = analyzer.analyze_position(pos)
    print_result(pos, result)
