#!/bin/bash

# change ehamon to your username

# export PATH=/home/ehamon/bin/anaconda3:$PATH

log=$(/home/ehamon/anaconda3/bin/python3 /home/ehamon/bin/bitwarden2lastpass.py $*)
/usr/bin/kdialog --title "bitwarden2lastpass" --msgbox "Log:\n\n${log}"
