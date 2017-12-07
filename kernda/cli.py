"""Adds conda environment activation to a Jupyter kernel spec."""
from __future__ import print_function

import argparse
import json
import os
import sys
from os.path import join as pjoin, dirname, isfile, expanduser
try:
    from shlex import quote
except ImportError:
    from pipes import quote


# This is the final form the kernel start command will take
# after running kernda. It's at the module-level for ease of reference only.
FULL_CMD_TMPL = 'source "{env_dir}/bin/activate" "{env_dir}" && exec {start_cmd} {start_args}'


def add_activation(args):
    """Add conda environment activation to a kernel spec.

    Parameters
    ----------
    args: Namespace
        argparse command line arguments

    Returns
    -------
    int
        Exit code
    """
    input_fn = args.kernelspec
    if not isfile(input_fn):
        print('Error: kernel spec {} not found'.format(args.kernelspec))
        return 1

    with open(input_fn) as f:
        spec = json.load(f)

    # Treat the path provided by the user as the conda environment we
    # want to activate. If the user did not provide a path, assume the
    # path containing the conda kernel is the desired environment.
    bin_dir = args.env_dir
    if not bin_dir:
        executable = spec['argv'][0]
        bin_dir = dirname(executable)
    elif bin_dir and not os.path.exists(bin_dir):
        print("Error: {} does not exist".format(bin_dir), file=sys.stderr)
        return 1

    # Add the bin subdir to the path if it's not already included.
    if not bin_dir.endswith('bin'):
        bin_dir += os.path.sep + 'bin'

    if not isfile(pjoin(bin_dir, 'activate')):
        print(spec)
        print('Error: {} does not contain a conda activate script'.format(bin_dir),
              file=sys.stderr)
        return 1

    env_dir = dirname(bin_dir)
    start_cmd = ' '.join(spec['argv'])
    full_cmd = FULL_CMD_TMPL.format(
        env_dir=env_dir,
        start_cmd=start_cmd,
        start_args=args.start_args)
    spec['argv'] = ['bash', '-c', quote(full_cmd)]

    if args.display_name:
        spec['display_name'] = args.display_name

    # Print the new kernel spec JSON to stdout for redirection
    print(json.dumps(spec, indent=2))

    # Overwrite the original if requested
    if args.overwrite:
        with open(input_fn, 'w') as f:
            json.dump(spec, f, indent=2)
        print('Wrote to {}'.format(input_fn), file=sys.stderr)

    return 0


def cli(argv=sys.argv[1:]):
    """Parse command line args and execute add_activation."""
    parser = argparse.ArgumentParser(description='')
    parser.add_argument('kernelspec', metavar='kernel.json',
                        help='Path to a kernel spec')
    parser.add_argument('--display-name', dest='display_name', type=str,
                        help='New display name for the kernel (default: keep '
                        'the original)')
    parser.add_argument('--overwrite', '-o', dest='overwrite',
                        action='store_const',
                        const=True, default=False,
                        help='Overwrite the existing kernel spec (default: '
                        'False, print to stdout')
    parser.add_argument("--env-dir", action="store", default=None,
                        help="Path to the conda environment that should "
                        "activate (default: prefix path to the "
                        "kernel in the existing kernel spec file)")
    parser.add_argument("--start-args", dest="start_args", type=str,
                        default='',
                        help="Additional arguments to append to the kernel "
                        "start command (default: '')")
    args, unknown = parser.parse_known_args(argv)
    return add_activation(args)


if __name__ == '__main__':
    sys.exit(cli())
