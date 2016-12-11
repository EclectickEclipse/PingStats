# Preamble and Technical Notes

This software aims to provide efficient ping visulaization via Python's
`matplotlib` via pure python implementations of the Ping protocol via
[python-ping](https://github.com/l4m3rx/python-ping).

Due to [python-ping's](https://github.com/l4m3rx/python-ping) use of raw
sockets, the software requires `sudo` permissions to generate ping packets. For
more detail please see the afore mentioned repository.

It can be used after the ping data has been collected without `sudo`.

## Installation of python-ping

Due to [python-ping's](https://github.com/l4m3rx/python-ping) use of a `-`
character in the package title, you need to install the software without the
`-` included in the folder title. 

This repository looks first for [python-ping](https://github.com/l4m3rx/python-ping) as a folder within the software's parent directory. For example:

```
-PingStats
|-pythonping/
|-pingstats repo files
```

This can be achieved by running `git clone` in the `PingStats` directory, and then renaming the resulting folder from `python-ping` to `pythonping`. 

---

## Running tests

The included `tests.py` module can be run for automatic testing of the
software run by [python's
hypothesis](https://github.com/HypothesisWorks/hypothesis-python). Follow the
instructions provided to install the software.

--- 

## Python Dependencies:

The software requires the following additional `Python` packages:

1. [matplotlib](http://matplotlib.org/) - installable via `pip install matplotlib` (pip install handles all requirements)

2. [python-ping](https://github.com/l4m3rx/python-ping) installed via above method.

3. [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) installable via `pip install hypothesis` (used for `tests.py`)


---

### USAGE


usage: main.py
	       [-h] [-a ADDRESS] [-d DELAY] [-gi] [-n NAME] [-p PATH]

               [-pf PLOTFILE] [-q] [-s] [-sF REFRESHFREQUENCY]

               [-sL TABLELENGTH] [-sNF] [-v]

PingStats Version 2.2 (C) Ariana Giroux, Eclectick Media Solutions. circa Sun
Dec 4 05:03:21 2016. This program defines some basic ping statistic
visualization methods through Python's 'matplotlib'.

Optional arguments:
  -h, --help            `show this help message and exit`

  -a ADDRESS, --address ADDRESS

                        The IP address to ping.

  -d DELAY, --delay DELAY

                        The interval of time (in seconds) to wait between ping
                        requests.

  -gi, --generateimage 

			Used in conjunction with the -pf option, this option
                        sends a name for a '*.png' file to save to the current
                        working directory.

  -n NAME, --name NAME  

			Flag this option to use a custom name for the CSV
                        output file.

  -p PATH, --path PATH  `The path to output csv files to`

  -pf PLOTFILE, --plotfile PLOTFILE

                        Include the path to a previously generated CSVfile to
                        generate a plot.

  -q, --quiet           `Flag this for quiet operation.`

  -s, --showliveplot    

			Flag this option to display an animated plot of the
                        last 500 ping sequences.

  -sF REFRESHFREQUENCY, --refreshfrequency REFRESHFREQUENCY

                        Specify a number of milliseconds to wait
                        betweenrefreshes of the -s plot visualization
                        feature.The lower the number, the better the
                        performanceof PingStats visualization. Handy for
                        "potatoes"

  -sL TABLELENGTH, --tablelength TABLELENGTH

                        The total number of pings to show for -s. Thelower the
                        number, the better the performance of PingStats
                        visualization. Handy for "potatoes."

  -sNF, --nofile        

			Flag this option to disable outputting ping
                        information to a csv file during live plotting. Helps
                        with memory consumption.

  -v, --version         `Flag this option to display software version.`


---

### Contribution

To contribute please open an issue or create a fork and submit a pull request
via *GitHub*
