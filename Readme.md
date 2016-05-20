# Installation

This utility can be installed on an *`*Nix`* machine by using the included distributable `install.sh`. This utility will
 autmatically install all the necessary dependencies for this software and copies it to your `/usr/local/bin` directory,
 enabling easy access to the software.
 
--------
 
On an *`NT`* Machine, you can use the included `install.bat` file in the selected distributable version. This utility 
 will autmatically copy the application to your `C:\WINDOWS\System32` directory, enabling easy access from the command 
 line inteface by typing 'pingstats'.
 
    This functionality will be present in V1.0. As of current, *NT* users must manually install the dependencies for 
    this application.

--------
    
### Windows manual build:

To build this application manually on an *`NT`* system, follow these steps:

1. Install `Python3.5.1` or higher,
2. Install `numpy` (a python package, available through `pip`),
3. Install `matplotlib` (a python package, available through `pip`),
4. Download the most recent `PingStats.py` to a local directory, and create a batch file that calls the `Python` 
interpreter you installed in step 1 and passes the local `PingStats.py` file.

--------

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
    