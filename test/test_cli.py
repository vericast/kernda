import os
import pexpect
import pytest
import shutil
import sys
from functools import namedtuple
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
    stdout = pexpect.run('/bin/bash -c "conda create -y -p {env_path} ipykernel && \
                          source activate {env_path} && \
                          python -m ipykernel install --user --name {name} && \
                          jupyter --data-dir"'.format(env_path=env_path, name=name))
    # jupyter user data path is at the end of the output
    user_path = stdout.decode('utf-8').split('\n')[-2].strip()
    # the kernel spec resides in the jupyter user data path
    spec_path = os.path.join(user_path, 'kernels', name)
    yield Kernel(name, os.path.join(spec_path, 'kernel.json'), env_path)
    shutil.rmtree(env_path)


def kernel_conda(kernel):
    """Run which conda in the test fixture kernel using Jupyter console."""
    jupyter = pexpect.spawn('jupyter', [
        'console',
        '--kernel', kernel.name]
    )
    jupyter.expect('In.*:')
    jupyter.sendline('!which conda')
    # input echo
    jupyter.readline()
    # path output
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
