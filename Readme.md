# PingStats

## PingStats Abstract

PingStats is a command line utility to create logs of ping statistics, and parse them back to the user in real(ish)
 time. Whilst being a command line utility, this program utilizes Python's "matplotlib" to make data visualization
 charts, thus creating a defacto GUI.

## PingStats build

This program makes use of Python's "matplotlib", which can be installed via a "pip install".

    "pip install matplotlib"
    
Due to the size and number of required packages for matplotlib, it makes the current build very large, and every 
execution must parse fonts as if it were the first exectuion. It may be prudent to look into other build options for 
*PingStats*...

The build script on PingStats is dependent on "PyInstaller", and can be installed using a "pip install".

    "pip install pyinstaller"
    
The build script also has support for MacOSx's "say" functionality. If you are not on MacOSx, you will need to comment 
these lines. By default, they are left uncommented.

    say "GIVEN TTS OUTPUT"
    
## PingStats contribution

To get involved in contributino to PingStats, please create a branch for your new feature or bugfix, and create pull
requests to the master to submit.
