# Installation

This script is meant to run on a `*NIX` OS, and as such provides a script for easy installation in ./dist/VERSION.zip/
install.sh. It will automatically install python and matplotlib, and creates an executable file in /usr/local/bin to 
enable easy use. 

Unpack the VERSION.zip file that you chose, and open a terminal in the directory you downloaded it to. Then from the 
terminal, enter `./install.sh`, and hope for the best!

## usage: pingstats

    [-h] [-a ADDRESS] [-g GURUSETTINGS] [-p PATH]
    [-pf PLOTFILE] [-gi GENERATEIMAGE] [-n NAME] [-s]
    [-sF REFRESHFREQUENCY] [-sL TABLELENGTH] [-sNF] [-v]

## optional arguments:

  -h, --help
              
    show this help message and exit
    
  -a ADDRESS, --address ADDRESS
  
    The IP address to ping.
    
  -g GURUSETTINGS, --gurusettings GURUSETTINGS
  
    For use by gurus: implement a custom argument to pass
    to the ping process.
    
  -p PATH, --path PATH
    
    To supply a specific path to output any files to,
    include a path.
    
  -pf PLOTFILE, --plotfile PLOTFILE
  
    Include the path to a previously generated CSV file to
    generate a plot.
    
  -gi GENERATEIMAGE, --generateimage GENERATEIMAGE
  
    Used in conjunction with the -pf option, this option
    sends a name for a '*.png' file to save to the current
    working directory.
    
  -n NAME, --name NAME
    
    Flag this option to use a custom name for the CSV
    output file.
    
  -s, --showliveplot
      
    Flag this option to display an animated plot of the
    last 500 ping sequences.
    
  -sF REFRESHFREQUENCY, --refreshfrequency REFRESHFREQUENCY
  
    Specify a number of milliseconds to wait between
    refreshesof the -s plot visualization feature. THe
    lower the number,the better the performance of
    PingStats visualization. Handy for"potatoes"
    
  -sL TABLELENGTH, --tablelength TABLELENGTH
  
    The total number of pings to show for -s. The lower
    the number, the better the performance of PingStats
    visulization. Handy for "potatoes."
    
  -sNF, --nofile        
  
    Flag this option to disable outputting ping
    information to a csv file during live plotting. Helps
    with memory consumption.
    
  -v, --version
           
    Flag this option to display software version.
    