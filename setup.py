
from setuptools import setup
import os
import pkg_resources

setup(
    name="caracol-tv",
    version="0.1",
    description='Script capturar la señal en vivo de Caracol Televisión',
    author="Leo",
    url="https://github.com/CalumRakk/caracoltv",
    install_requires=[
        str(r)
        for r in pkg_resources.parse_requirements(
            open(os.path.join(os.path.dirname(__file__), "requirements.txt"))
        )
    ],
    entry_points={
        "console_scripts": ["caracoltv=caracoltv.script:schedule"],
    },
    packages=['caracoltv'],
)
