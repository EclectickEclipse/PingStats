# Preamble and Technical Notes

This software aims to provide efficient ping visualization via Python's `matplotlib` via pure python implementations of the Ping protocol via [python-ping](https://github.com/l4m3rx/python-ping).

Due to [python-ping's](https://github.com/l4m3rx/python-ping) use of raw sockets, the software requires `sudo` permissions to generate ping packets. For more detail please see the afore mentioned repository.

It can be used after the ping data has been collected without `sudo` to display a plot of the CSV data gathered (the `-pf` and `-gi` arguments).

## Installation of python-ping

Due to [python-ping's](https://github.com/l4m3rx/python-ping) use of a `-` character in the package title, you need to install the software without the `-` included in the folder title. 

This repository looks for pythonping as a folder within the software's parent directory to load [python-ping](https://github.com/l4m3rx/python-ping). For example:

```
-PingStats
|-pythonping/
|-pingstats repo files
```

This can be achieved by running the following command from within the repository's local directory:

```sh
git clone https://github.com/l4m3rx/python-ping.git pythonping
```

This may be fixed soon, due to an [ongoing discussion on repo naming](https://github.com/l4m3rx/python-ping/issues/23)

---

## Running tests

The included `tests.py` module can be run for automatic testing of the
software run by [python's hypothesis](https://github.com/HypothesisWorks/hypothesis-python). Follow the instructions provided to install the software.

Please note, as of `V2.4` these tests are broken, and will not work. See #89 for reference.

--- 

## Python Dependencies:

The software requires the following additional `Python` packages:

1. [matplotlib](http://matplotlib.org/) - installable via `pip install matplotlib` (pip install handles all requirements)

2. [python-ping](https://github.com/l4m3rx/python-ping) installed via above method.

3. [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) installable via `pip install hypothesis` (used for tests)


---

### USAGE

To use the software's UI, you can either supply command line arguments, or simply run `main.py`

usage: main.py 

		       [-h] [-a ADDRESS] [-d DELAY] [-t TIMEOUT] [-gi GENERATEIMAGE]
	
		       [-n NAME] [-p PATH] [-pf PLOTFILE] [-q] [-s] [-c]
	
		       [-sF REFRESHFREQUENCY] [-sL TABLELENGTH] [-sNF] [-v]

PingStats Version 2.4 (C) Ariana Giroux, Eclectick Media Solutions. circa Tue
May 23 17:01:17 2017. This program defines some basic ping statistic
visualization methods through Python's 'matplotlib'.

optional arguments:

  -h, --help            
  
  			show this help message and exit
  
  -a ADDRESS, --address ADDRESS
  
                        The IP address to ping.
			
  -d DELAY, --delay DELAY
  
                        The interval of time (in seconds) to wait between ping
                        requests.
			
  -t TIMEOUT, --timeout TIMEOUT
  
                        The amount of time to set for each packets' timeout.
			
  -gi GENERATEIMAGE, --generateimage GENERATEIMAGE
  
                        Used in conjunction with the -pf option, this option
                        sends a name for a '*.png' file to save to the current
                        working directory.
			
  -n NAME, --name NAME  
  
  			Flag this option to use a custom name for the CSV
                        output file.
			
  -p PATH, --path PATH  
  			The path to output csv files to
			
  -pf PLOTFILE, --plotfile PLOTFILE
  
                        Include the path to a previously generated CSVfile to
                        generate a plot.
			
  -q, --quiet           
  
  			Flag this for quiet operation.
  -s, --showliveplot    
  
  			Flag this option to display a live plot of return time
                        (in ms) by time received. Use this command to skip the
                        UI entirely.
			
  -c, --cli             
  
  			Flag this option if you want to skip running the UI
                        entirely, and instead just rely on CLI arguments.
			
  -sF REFRESHFREQUENCY, --refreshfrequency REFRESHFREQUENCY
  
                        Specify a number of milliseconds to wait
                        betweenrefreshes of the -s plot visualization
                        feature. The lower the number, the better the
                        performance of PingStats visualization. Handy for
                        "potatoes"
			
  -sL TABLELENGTH, --tablelength TABLELENGTH
  
                        The total number of pings to show for -s. Thelower the
                        number, the better the performance of PingStats
                        visualization. Handy for "potatoes."
			
  -sNF, --nofile        
  
  			Flag this option to disable outputting ping
                        information to a csv file during live plotting. Helps
                        with memory consumption.
			
  -v, --version         
  			
			Flag this option to display software version.

---

### Contribution

To contribute please open an issue or create a fork and submit a pull request via *GitHub*

---

### Bug reporting

To report a bug or broken execution please follow these steps.

1. Open a new issue on
   [GitHub](https://github.com/EclectickMedia/PingStats/issues)
2. Describe your bug in as good a description as possible
3. Run `tests.py` and attach the results to the new issue.

Alternatively, if you do not have github, write an email to
`ariana.giroux@gmail.com` and attach the previously mentioned
information.
