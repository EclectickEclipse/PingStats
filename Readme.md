# Installation

This script is meant to run on a `*NIX` OS, and as such provides a script for easy installation in ./dist/<version>.zip/
install.sh. It will automatically install python and matplotlib, and creates an executable file in /usr/local/bin to 
enable easy use. 

Unpack the <version>.zip file that you chose, and open a terminal in the directory you downloaded it to. Then from the 
terminal, enter `./install.sh`, and hope for the best!

## usage: pingstats.py

    `[-h] [-a ADDRESS] [-c CUSTOMARG] [-d DESTINATION]`
    `[-F PINGFREQUENCY] [-n NAME] [-t TIME] [-v] [-s]`
    `[-sF REFRESHFREQUENCY] [-sL TABLELENGTH]`

## optional arguments:
  -h, --help            
  
    show this help message and exit
    
  -a ADDRESS, --address ADDRESS
  
    The IP address to ping.
    
  -c CUSTOMARG, --customarg CUSTOMARG
  
    Define your own argument for the ping. If you are experiencing issues with pings ending before intended,try using 
    '-c "-c 999999999"' to spawn a process with an extremely long runtime.
  -d DESTINATION, --destination DESTINATION
  
    To supply a specific path to output any files to, include a path.
  -F PINGFREQUENCY, --pingfrequency PINGFREQUENCY
  
    The frequency with which to ping the host. Defaults to 0.25 seconds.
    
  -n NAME, --name NAME  
  
    Flag this option to use a custom name for the CSV output file.
    
  -t TIME, --time TIME  
  
    The time to wait before killing the process in seconds.
    
  -v, --version         
  
    Flag this option to display software version.
    
  -s, --showplot        
  
    Flag this option to display an animated plot of the last 500 ping sequences.
    
  -sF REFRESHFREQUENCY, --refreshfrequency REFRESHFREQUENCY
  
    Specify a number of milliseconds to wait between refreshes of the -s plot visualization feature. The lower the 
    number,the better the performance of PingStats visualization. Handy for "potatoes"
    
  -sL TABLELENGTH, --tablelength TABLELENGTH
  
    The total number of pings to show for -s. The lower the number, the better the performance of PingStats 
    visualization. Handy for "potatoes."
