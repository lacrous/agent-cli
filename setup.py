#!/usr/bin/env python3
"""Packaging setup for mika CLI."""

from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="mika-cli",
    version="0.1.0",
    author="lacrous",
    author_email="",
    description="A terminal-based open-source AI agent CLI with streaming and thinking display.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/lacrous/agent-cli",
    packages=find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Environment :: Console",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    entry_points={
        "console_scripts": [
            "mika=mika.cli:main",
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
