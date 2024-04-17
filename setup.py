from setuptools import setup
import os
import pkg_resources

setup(
    name="caracoltv",
    version="0.0.3",
    description="Script capturar la señal en vivo de Caracol Televisión",
    long_description=open("README.md", encoding="utf-8").read(),
    long_description_content_type="text/markdown",
    readme="README.md",
    author="Leo",
    url="https://github.com/CalumRakk/caracoltv",
    install_requires=["m3u8==3.4.0", "requests==2.28.2"],
    entry_points={
        "console_scripts": ["caracoltv=caracoltv.cli:run_script"],
    },
    packages=["caracoltv"],
)
