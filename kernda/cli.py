"""Adds conda environment activation to a Jupyter kernel spec."""
from __future__ import print_function

import argparse
import json
import os
import sys
import subprocess
from os.path import join as pjoin, dirname, isfile, expanduser, abspath
try:
    from shlex import quote
except ImportError:
    from pipes import quote


# This is the final form the kernel start command will take
# after running kernda. It's at the module-level for ease of reference only.

FULL_CMD_TMPL = '{source_or_conda} "{activate_script}" "{env_dir}" && exec {start_cmd} {start_args}'


def determine_conda_activate_script(env_dir):
    """Finds the correct path to an activate script.

    If no activate script exists or conda is broken / nonexistant this function will raise

    Parameters
    ----------
    env_dir : str
        path to an environment root

    Returns
    -------
    str
        Absolute path to a $PREFIX/bin/activate script

    """
    in_env = pjoin(env_dir, 'bin', 'activate')
    # virtualenv / conda < 4.4
    if os.path.exists(in_env):
        return abspath(in_env)
    # conda 4.4+ when something has been activated
    conda_executable_from_env = os.getenv('CONDA_EXE')
    if conda_executable_from_env:
        conda_prefix = abspath(pjoin(dirname(conda_executable_from_env), '..'))
    else:
        # conda 4.4+ when nothing is activated
        output = subprocess.check_output(['conda', 'info', '--json'])
        if sys.version_info[0] >= 3:
            output = output.decode('utf8')

        conda_prefix = json.loads(output).get("conda_prefix")
    if not conda_prefix:
        raise ValueError("No conda prefix could be determined")

    return abspath(pjoin(conda_prefix, 'bin', 'activate'))


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
    original_argv = spec.get("_kernda_original_argv") or spec['argv']
    if not bin_dir:
        executable = original_argv[0]
        bin_dir = dirname(executable)
    elif bin_dir and not os.path.exists(bin_dir):
        print("Error: {} does not exist".format(bin_dir), file=sys.stderr)
        return 1

    # Add the bin subdir to the path if it's not already included.
    if not bin_dir.endswith('bin'):
        bin_dir += os.path.sep + 'bin'

    # Retrieve the activate script associated with this environment.
    # This will return {bin_dir}/activate if it exists (conda<4.4, base env or virtualenv), otherwise it will fall back
    # to the activate script in the current base conda environment.
    #
    # In versions of conda > 4.4 environments no longer have their own activate script and rely on the base env
    # In prior versions of conda this was a symlink in any case to the base env's activate script
    try:
        activate_script = determine_conda_activate_script(pjoin(bin_dir, '..'))
    except (subprocess.CalledProcessError, ValueError):
        print("Error: Could not determine the location of the activation script associated with {}".format(bin_dir),
              file=sys.stderr)
        print("       Verify that the `conda` command works in your current shell by running `conda --info`",
              file=sys.stderr)
        return 1
    # Use source activate or conda activate, depending on the CLI flag
    source_or_conda = "conda" if args.conda_activate else "source"
    env_dir = dirname(bin_dir)
    start_cmd = ' '.join(quote(x) for x in original_argv)
    full_cmd = FULL_CMD_TMPL.format(
        source_or_conda=source_or_conda,
        activate_script=activate_script,
        env_dir=env_dir,
        start_cmd=start_cmd,
        start_args=args.start_args)
    spec['argv'] = ['bash', '-c', full_cmd]
    spec['_kernda_original_argv'] = original_argv

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
    parser.add_argument("--conda-activate", type=bool,
                        default=False,
                        help=("Use 'conda /path/to/activate' (when True) or "
                              "'source /path/to/activate' (when False). Defaults to "
                              "False"))

    args, unknown = parser.parse_known_args(argv)
    return add_activation(args)


if __name__ == '__main__':
    sys.exit(cli())
