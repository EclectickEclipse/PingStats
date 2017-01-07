# Preamble and Technical Notes

This software aims to provide efficient ping visulaization via Python's
`matplotlib` via pure python implementations of the Ping protocol via
[python-ping](https://github.com/l4m3rx/python-ping).

Due to [python-ping's](https://github.com/l4m3rx/python-ping) use of raw
sockets, the software requires `sudo` permissions to generate ping packets. For
more detail please see the afore mentioned repository.

It can be used after the ping data has been collected without `sudo`.

# Kivy Branch

This branch attempts to provide a different backend than matplotlib for
visualizing ping information, allowing us to compile and release an executable
for most major OS's.

This feature set is being developed due to a request from
[frawst](https://github.com/frawst)

### Kivy installation

Due to the use of a different backend than matplotlib, there are a few extra
steps to install and compile from source in this branch.

1. Install `Kivy`
   - Follow [these
     instructions](https://kivy.org/docs/installation/installation.html)

2. Create a `virtual environment` for `Kivy`
   - via `$ kivy -m venv venv`
   
   Calling `kivy -m` enables you to run a module in the `Python` environment,
   here we select `venv` *(short for virtual environment)*, and pass it a name
   for the resulting `virtual environment`. *(in this case we use venv for
   short)*

3. Activate the `virtual environment` we just created.
   - via `$ source venv/bin/activate`

   To leave the virtual environment, use `$ deactivate`

3. Install `garden.matplotlib` to the `venv` *(graph graphical backend)*.
   - via `$ garden install --app matplotlib`
   
   We will include the `--app` flag to instruct `Kivy` to only install the
   backend for **this** app.

4. Install `python-ping` as per the following instructions.

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

This may be fixed soon, due to an [ongoing discussion on repo
naming](https://github.com/l4m3rx/python-ping/issues/23)

---

## Running tests

Due to `Kivy`'s runtime not working with python's `unittest`, the tests have
been removed from this branch.

--- 

## Python Dependencies:

The software requires the following additional `Python` packages:

1. [matplotlib](http://matplotlib.org/) - installable via `pip install matplotlib` (pip install handles all requirements)

2. [python-ping](https://github.com/l4m3rx/python-ping) installed via above method.

3. [hypothesis](https://github.com/HypothesisWorks/hypothesis-python) installable via `pip install hypothesis` (used for `tests.py`)

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
