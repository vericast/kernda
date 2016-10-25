# kernda

Updates an IPython kernel.json so that it activates its conda environment before launching the kernel process.

## Requirements

* bash (i.e., does not yet work for kernels on Windows)

## Install

For the moment, install directly from GitHub.

`pip install git+https://github.com/parente/kernda`

## Usage

```
usage: kernda [-h] [--display_name DISPLAY_NAME] [--overwrite] [--yes]
              [--conda-env CONDA_ENV]
              kernel.json

positional arguments:
  kernel.json           Kernel spec for a kernel in a conda environment

optional arguments:
  -h, --help            show this help message and exit
  --display_name DISPLAY_NAME
                        New display name for the kernel
  --overwrite, -o       Overwrite the existing kernel spec (default: False,
                        make a new kernel spec)
  --yes, -y             Answer yes to all prompts
  --conda-env CONDA_ENV
                        Path to the conda environment that you would like to
                        use.
```

### Examples

```
# add activation of the current conda environment to an existing kernel.json
kernda ~/.local/share/jupyter/kernels/my_kernel/kernel.json -o

# shortcut for the above
kernda my_kernel -o

# add activation of my_environment to an existing kernel.json
kernda my_kernel --conda-env ~/miniconda/envs/my_environment -o -y

# redirect the kernel name from stdout to a new file instead of overwriting
kernda my_kernel > other_kernel.json
```
