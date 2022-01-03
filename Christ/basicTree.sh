#!/bin/bash
trap "tput reset; tput cnorm; exit" 2
clear
tput civis
while true; do
    clear
    /bin/python3 /home/kali/code/Christ/basicTree.py
    sleep 1
done