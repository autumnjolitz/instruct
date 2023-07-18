from codecs import open  # To use a consistent encoding
from os import path

# Always prefer setuptools over distutils
from setuptools import setup, find_packages

here = path.abspath(path.dirname(__file__))
install_requirements = [
    "Jinja2>=3.0.0,<4.0.0a0",
    "inflection<1.0.0a0",
    "typing-extensions>=4.2.0,<5.0.0a0",
]

with open(path.join(here, "README.rst"), encoding="utf-8") as fh:
    long_description = fh.read()

# We separate the version into a separate file so we can let people
# import everything in their __init__.py without causing ImportError.
__version__ = None
exec(open("instruct/about.py").read())
if __version__ is None:
    raise IOError("about.py in project lacks __version__!")


TEST_REQUIREMENTS = ["pytest", "pytest-mock"]
DEVEL_REQUIREMENTS = ["twine"] + TEST_REQUIREMENTS

setup(
    name="instruct",
    version=__version__,
    author="Autumn Jolitz",
    description="",
    long_description=long_description,
    license="BSD",
    packages=find_packages(exclude=["contrib", "docs", "tests*"]),
    include_package_data=True,
    install_requires=install_requirements,
    keywords=[],
    extras_require={"test": TEST_REQUIREMENTS, "devel": DEVEL_REQUIREMENTS},
    python_requires=">=3.7",
    url="https://github.com/autumnjolitz/instruct",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Topic :: Utilities",
        "License :: OSI Approved :: BSD License",
    ],
)
