#!/bin/zsh
cd "${0:A:h}"
python3 cars/tororosso/install_update.py
install_status=$?
echo
if [[ $install_status -ne 0 ]]; then
  echo 'Update not installed. Read the message above.'
fi
read -r '?Press Return to close.'
exit $install_status
