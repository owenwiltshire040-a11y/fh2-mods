#!/bin/zsh
cd "${0:A:h}"
"./build/Car Studio Capture.app/Contents/MacOS/CapturePreview" --request-access
printf '\nAllow Car Studio Capture in macOS Screen Recording settings, then try Capture preview again.\n'
