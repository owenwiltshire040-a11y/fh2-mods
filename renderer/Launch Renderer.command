#!/bin/zsh
cd "${0:A:h}"
python3 renderer.py showroom --lean-boot
printf '\nThe renderer experiment uses the game window. Close that window when finished.\n'
