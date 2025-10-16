"""Setup script for the Tetr_cli package."""
# coding: utf-8

from setuptools import setup, find_packages

setup(
    name="Tetr_cli",
    version="0.8.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["Tetr_cli = Tetr_cli.starter:starter"]},
    install_requires=[
        "ansicon>=1.89.0",
        "jinxed>=1.3.0",
        "keyboard>=0.13.5",
        "pygame>=2.6.1",
        "wcwidth>=0.2.13",
        "windows-curses>=2.4.1",
    ],
    include_package_data=True,
    package_data={
        "Tetr_cli": [
            "tetr_modules/sounds/sfx/*.wav",
            "tetr_modules/sounds/bgm/*.wav",
            "tetr_modules/sounds/sfx/*.ftm",
            "tetr_modules/sounds/bgm/*.ftm",
        ],
    },
    author="Airun_Iru",
)

if __name__ == "__main__":
    print("Setup script for Tetr_cli package.")
