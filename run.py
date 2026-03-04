#!/usr/bin/env python
import os, sys

_root = os.path.dirname(os.path.abspath(__file__))
for _d in ('', 'core', 'config'):
    _p = os.path.join(_root, _d) if _d else _root
    if _p not in sys.path:
        sys.path.insert(0, _p)

from app import app

if __name__ == '__main__':
    print('AAMUSTED Counselling System - http://localhost:5000')
    app.run(debug=True, host='127.0.0.1', port=5000)
