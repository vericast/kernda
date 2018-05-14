import os
import subprocess
import pexpect
import pytest
import shutil
import sys
from collections import namedtuple
from kernda.cli import cli
from tempfile import gettempdir
from uuid import uuid4

Kernel = namedtuple('Kernel', ['name', 'spec', 'env'])

@pytest.fixture(scope='function')
def kernel():
    """Create a ipykernel conda environment separate from this test
    environment where jupyter console is installed.

    The environments must be separate otherwise we cannot easily check
    if kernel start is activating the environment or if it was already
    active when the test suite started.
    """
    # unique name for the kernel and environment
    name = str(uuid4())
    env_path = '{}/kernel-env-{name}'.format(gettempdir(), name=name)
    stdout = subprocess.check_output(
        ["conda", "create", "--yes", "--quiet", "--prefix", env_path, "python=3.6", "ipykernel"])

    stdout = pexpect.run('/bin/bash -c "source activate {env_path} && \
                python -m ipykernel install --user \
                --name {name}"'.format(env_path=env_path, name=name))
    # query jupyter for the user data directory in a separate command to
    # make parsing easier
    stdout = pexpect.run('jupyter --data-dir')
    user_path = stdout.decode('utf-8').strip()
    # the kernel spec resides in the jupyter user data path
    spec_path = os.path.join(user_path, 'kernels', name)
    yield Kernel(name, os.path.join(spec_path, 'kernel.json'), env_path)
    shutil.rmtree(env_path)


def kernel_conda(kernel):
    """Run which conda in the test fixture kernel using Jupyter console."""
    jupyter = pexpect.spawn('jupyter', [
        'console',
        '--simple-prompt',
        '--kernel', kernel.name]
    )
    jupyter.expect('In.*:')
    jupyter.sendline('json_data = !conda info --json')
    # input echo
    jupyter.readline()
    out = jupyter.readline()

    jupyter.expect('In.*:')
    jupyter.sendline('import json; json_data = json.loads("".join(json_data))')
    # input echo
    jupyter.readline()
    out = jupyter.readline()

    jupyter.expect('In.*:')
    jupyter.sendline('json_data["active_prefix"]')
    # input echo
    jupyter.readline()# path output
    path = jupyter.readline()

    jupyter.close()
    return path.decode('utf-8')


def test_original_spec(kernel):
    """The kernel should output a conda path in the test suite environment.

    More of a test of the complicated logic in the test fixture than
    anything, but it ensures a a good test baseline.
    """
    stdout = pexpect.run('which conda')
    conda_path = stdout.decode('utf-8').strip()
    assert conda_path.startswith(sys.prefix)


def test_overwritten_spec(kernel):
    """The kernel should output a conda path in its own environment."""
    rv = cli(['-o', kernel.spec])
    assert rv == 0
    assert kernel.env in kernel_conda(kernel)


def test_start_args(kernel):
    """The kernel spec should include additional arguments."""
    rv = cli(['-o', kernel.spec, '--start-args=--Completer.use_jedi=False'])
    assert rv == 0
    assert kernel.env in kernel_conda(kernel)
