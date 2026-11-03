#!/bin/zsh
cd "${0:A:h}"
python3 renderer.py status
python3 refresh.py --status
python3 renderer.py verify
read '?Press Return to close.'
