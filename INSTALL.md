This page summarizes PyPoi installation steps.
PyPoi is uploaded to PyPI, which means that you can install it via `pip install pypoi` command.

If you encounter an issue, please raise a new issue following the [Reporting issues](#reporting-issues) section.

### With Anaconda (recommended)
1. Download and install latest Anaconda (Python 3.x) from https://www.anaconda.com/distribution/
2. The following commands will create a conda environment and install PyPoi on it.
```
# Crate a new conda environment
conda create -n pypoi python=3

# Activate the environment
conda activate pypoi

# Install PyPoi
pip install pypoi

# Launch Pypoi
pypoi
```

### With the official Python distribution
TODO: Write

### With the MacOS System Default Python
Assuming the following two commands return the following outputs.
```
~ which python
/usr/bin/python
~ which pip
/usr/local/bin/pip
```
To install PyPoi, run
```
sudo pip install pypoi
```
To launch PyPoi, run
```
pypoi
```

## Reporting issues
Having trouble installing pypoi? 
I'd appreciate if you raise a new issue in the [issues page](https://github.com/fbessho/PyPoi/issues) with the following details.

* OS
* OS version
* Python distribution to be used (System default, Anaconda, Python.org)
* Steps you went through and error message(s) you got
