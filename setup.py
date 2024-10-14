from setuptools import setup, find_packages

setup(
    name="pycaracoltv",
    version="0.4.0",
    url="https://github.com/CalumRakk/pycaracoltv",
    description="pycaracoltv es una herramienta de web scraping para extraer videos, imágenes y otros tipos de metadatos de la página caracoltv.com",
    author="Leo",
    author_email="leocasti2@gmail.com",
    packages=find_packages(),
    install_requires=["lxml", "requests"],
)
