# kernda

[![Build Status](https://travis-ci.org/maxpoint/kernda.svg?branch=master)](https://travis-ci.org/maxpoint/kernda)
[![PyPI version](https://badge.fury.io/py/kernda.svg)](https://badge.fury.io/py/kernda)
[![codecov](https://codecov.io/gh/maxpoint/kernda/branch/master/graph/badge.svg)](https://codecov.io/gh/maxpoint/kernda)

Updates an IPython or IRKernel kernel spec (i.e., kernel.json file) to activate a conda environment before launching the kernel process.

## Requirements

* bash (i.e., does not yet work for kernels on Windows)

## Install

`pip install kernda`

## Usage

```
usage: kernda [-h] [--display-name DISPLAY_NAME] [--overwrite]
              [--env-dir ENV_DIR]
              kernel.json

positional arguments:
  kernel.json           Path to a kernel spec

optional arguments:
  -h, --help            show this help message and exit
  --display-name DISPLAY_NAME
                        New display name for the kernel (default: keep the
                        original)
  --overwrite, -o       Overwrite the existing kernel spec (default: False,
                        print to stdout
  --env-dir ENV_DIR     Path to the conda environment that should activate
                        (default: prefix path to the kernel in the existing
                        kernel spec file)
```

### Examples

```
# modify the kernel spec in place so that it activates the conda
# environment containing the kernel binary
kernda ~/.local/share/jupyter/kernels/my_kernel/kernel.json -o

# print the modified kernel spec to stdout and redirect it
# to a new file
kernda /usr/local/share/jupyter/kernels/my_kernel/kernel.json > other_kernel.json

# modify the kerne spec in place so that it activates the
# specified conda environment
kernda ~/some_kernel.json -o --env-dir ~/envs/my_env
```
