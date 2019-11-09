import setuptools
from statsapi import version

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MLB-StatsAPI",
    version=version.VERSION,
    author="Todd Roberts",
    author_email="todd@toddrob.com",
    description="MLB Stats API Wrapper for Python",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/toddrob99/MLB-StatsAPI",
    packages=setuptools.find_packages(),
    install_requires=["requests"],
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: OS Independent",
    ],
)
