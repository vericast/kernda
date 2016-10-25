from __future__ import print_function

import argparse
import errno
import json
import os
import sys
from os.path import join as pjoin, dirname, isfile, expanduser

try:
    input = raw_input
except NameError:
    # python3: input exists, raw_input does not
    pass


def mkdir_p(path):
    '''Python2/3 mkdir -p'''
    try:
        os.makedirs(path)
    except OSError as ex:
        if ex.errno == errno.EEXIST and os.path.isdir(path):
            pass
        else:
            raise

# we don't want a dep on jupyter, so here's a hardcode
USER_KERNELS = expanduser('~/.local/share/jupyter/kernels')
# form of our activation command
FULL_CMD_TMPL = 'source "{env_dir}/bin/activate" "{env_dir}" && exec {start_cmd}'


def prompt(text):
    '''Prompt for y or n and return True if y.'''
    print(text + ' [y/N]', end=' ', file=sys.stderr)
    resp = input().lower()
    return resp == 'y'


def add_activation(args):
    # shortcut for a kernelspec name in the user's home dir
    input_fn = pjoin(USER_KERNELS, args.kernelspec, 'kernel.json')
    if isfile(args.kernelspec):
        # let a relative or full path reference to a kernel spec
        # trump th user home dir shortcut
        input_fn = args.kernelspec
    elif not isfile(input_fn):
        print('Kernel spec {} not found'.format(args.kernelspec))
        return 1

    with open(input_fn) as f:
        spec = json.load(f)

    bin_dir = args.conda_env
    if bin_dir and not os.path.exists(bin_dir):
        print("{} does not exist".format(bin_dir), file=sys.stderr)
        print("Aborting kernda", file=sys.stderr)
        return 1

    if not bin_dir or not os.path.exists(bin_dir):
        # this is the default behavior
        print("Getting bin_dir from the kernel spec", file=sys.stderr)
        executable = spec['argv'][0]
        bin_dir = dirname(executable)

    if not bin_dir.endswith('bin'):
        bin_dir += os.path.sep + 'bin'
    print("bin_dir={}".format(bin_dir), file=sys.stderr)

    if not isfile(pjoin(bin_dir, 'activate')):
        print(spec)
        print('''
Error: Kernel spec does not appear to be using a Python from a conda environment,
the conda environment is not found, or the kernel spec is already activating the
conda environment.

Aborted''', file=sys.stderr)
        return 1

    env_dir = dirname(bin_dir)
    start_cmd = ' '.join(spec['argv'])
    full_cmd = FULL_CMD_TMPL.format(env_dir=env_dir, start_cmd=start_cmd)
    spec['argv'] = ['bash', '-c', full_cmd]

    if args.display_name:
        spec['display_name'] = args.display_name

    # print to stdout so it can be redirected to a file
    print(json.dumps(spec, indent=2))

    if args.overwrite:
        if args.yes or prompt('\nOverwrite the original kernel spec?'):
            with open(input_fn, 'w') as f:
                json.dump(spec, f, indent=2)
            print('Wrote to {}'.format(input_fn), file=sys.stderr)
        else:
            print('Aborted', file=sys.stderr)

    return 0


def cli():
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('kernelspec', metavar='kernel.json',
                        help='kernel spec for a kernel in a conda environment')
    parser.add_argument('--display_name', dest='display_name', type=str,
                        help='new display name for the kernel')
    parser.add_argument('--overwrite', '-o', dest='overwrite', action='store_const',
                        const=True, default=False,
                        help='overwrite the existing kernel spec (default: False, make a new kernel spec)')
    parser.add_argument('--yes', '-y', dest='yes', action='store_const',
                        const=True, default=False,
                        help='answer yes to all prompts')
    parser.add_argument("--conda-env", action="store", default=None,
                        help=("Path to the conda environment that you would like to use."))
    args = parser.parse_args()
    rv = add_activation(args)
    sys.exit(rv)

if __name__ == '__main__':
    cli()
