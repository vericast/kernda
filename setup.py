import versioneer
from setuptools import setup

setup_args = dict(
    name='kernda',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='Add conda environment activation to an IPython kernel spec',
    url='https://github.com/Valassis-Digital-Media/kernda',
    author='Valassis Digital',
    maintainer='Valassis Digital',
    maintainer_email='ParenteP@valassis.com',
    license='BSD 3-Clause',
    platforms=['Linux', 'Mac OSX'],
    packages=['kernda'],
    entry_points={
        'console_scripts': ['kernda = kernda.cli:cli']
    }
)

if __name__ == '__main__':
    setup(**setup_args)
