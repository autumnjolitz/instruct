import sys
from codecs import open  # To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import (setup, find_packages)

here = path.abspath(path.dirname(__file__))
install_requirements = [
    # Place your project requirements here.

    # One way to keep up-to-date while still keeping a stable API is to
    # use semantic versioning. If the requirement has a major.minor.[bugfix] format,
    # then you can restrict versions by range. Suggest you read
    # `PEP 440<https://www.python.org/dev/peps/pep-0440/>`_ for more information.

    # Example where we ask for a ``fake`` library and block a specific version.
    # 'fake>=1.0.0, !1.1.0, <2.0.0a0'
]

# The following are meant to avoid accidental upload/registration of this
# package in the Python Package Index (PyPi)
pypi_operations = frozenset(['register', 'upload']) & frozenset([x.lower() for x in sys.argv])
if pypi_operations:
    raise ValueError('Command(s) {} disabled in this example.'.format(', '.join(pypi_operations)))

# Python favors using README.rst files (as opposed to README.md files)
# If you wish to use README.md, you must add the following line to your MANIFEST.in file::
#
#     include README.md
#
# then you can change the README.rst to README.md below.
with open(path.join(here, 'README.rst'), encoding='utf-8') as fh:
    long_description = fh.read()

# We separate the version into a separate file so we can let people
# import everything in their __init__.py without causing ImportError.
__version__ = None
exec(open('instruct/about.py').read())
if __version__ is None:
    raise IOError('about.py in project lacks __version__!')

setup(name='instruct', version=__version__,
      author='Ben Jolitz',
      description='',
      long_description=long_description,
      license='BSD',
      packages=find_packages(exclude=['contrib', 'docs', 'tests*']),
      include_package_data=True,
      install_requires=install_requirements,
      keywords=[],
      python_requires='>=3',
      url="https://github.com/benjolitz/instruct",
      classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
      ])
