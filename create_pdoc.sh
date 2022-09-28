#!/bin/bash
pip3 install pdoc3
pdoc3 --html --output-dir docs pedantic --force
"docs/pedantic/index.html"
