
# Instructions

Clone this repository with `git clone --recurse-submodules https://github.com/TheCDC/cbu_homecoming_2018`

## Installing Dependencies

If you didn't use the above command, initialize/fetch submodules:
```
git submodule init
git submodule update
```

I wrote these commands for my linux system(s), but they should work on Windows as well, although instances of `python3` might need to be replaced with `python`.


Execute these commands from the repo root.

```
pip3 install --user pipenv
pipenv --python 3.6
pipenv install
pipenv shell

```
Doing so will install all dependencies in a virtual environment.

`pipenv shell` puts your shell in a context where the dependencies are accessible.


## Markov Demo
```
sudo apt install graphviz
```

Execute it (while in pipenv shell) with `python markov.py`. Doing so should automatically open a browser tab pointed to the web interface. Further instructions are within said interface.

Close it as a normal console application by either closing the console window or otherwise killing the process.

## Evil RPS Demo

This shares dependencies with the Markov demo.

TODO: implement GUI, write execution instructions.


## N-Body Physics Simulation

TODO: installation and execution instructions.
