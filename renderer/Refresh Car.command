#!/bin/zsh
cd "${0:A:h}"
python3 refresh.py --configured
read '?Press Return to close, then return to the car view.'
