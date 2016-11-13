### USAGE

---

Usage: PingStats.py [-h] [-a ADDRESS] [-p PATH] [-pf PLOTFILE]
                    [-gi GENERATEIMAGE] [-n NAME] [-s] [-sF REFRESHFREQUENCY]
                    [-sL TABLELENGTH] [-sNF] [-v]

PingStats Version 2.0.01 (C) Ariana Giroux, Eclectick Media Solutions. circa
Sun Nov 13 06:39:04 2016. This program defines some basic ping statistic
visualization methods through Python's 'matplotlib'.

Optional arguments:
  -h, --help            show this help message and exit
  -a ADDRESS, --address ADDRESS
                        The IP address to ping.
  -p PATH, --path PATH  The path to output csv files to
  -pf PLOTFILE, --plotfile PLOTFILE
                        Include the path to a previously generated CSVfile to
                        generate a plot.
  -gi GENERATEIMAGE, --generateimage GENERATEIMAGE
                        Used in conjunction with the -pf option, this option
                        sends a name for a '*.png' file to save to the current
                        working directory.
  -n NAME, --name NAME  Flag this option to use a custom name for the CSV
                        output file.
  -s, --showliveplot    Flag this option to display an animated plot ofthe
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
  -sNF, --nofile        Flag this option to disable outputting ping
                        information to a csv file during live plotting. Helps
                        with memory consumption.
  -v, --version         Flag this option to display software version.

---

### Contribution

To contribute please open an issue or create a fork and submit a pull request
via *GitHub*
