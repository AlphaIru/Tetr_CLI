"""Setup script for the tetr_cli package."""

# coding: utf-8

from setuptools import setup, find_packages

setup(
    name="tetr_cli",
    version="0.8.0",
    packages=find_packages(),
    entry_points={"console_scripts": ["tetr_cli = tetr_cli.starter:starter"]},
    python_requires=">=3.7",
    install_requires=[
        "ansicon>=1.83.0",
        "jinxed>=1.1.0",
        "keyboard>=0.13.3",
        "pygame>=2.1.2",
        "wcwidth>=0.1.7",
        "windows-curses>=2.2.0",
    ],
    include_package_data=True,
    package_data={
        "tetr_cli": [
            "tetr_modules/sounds/sfx/*.wav",
            "tetr_modules/sounds/bgm/*.wav",
            "tetr_modules/sounds/sfx/*.ftm",
            "tetr_modules/sounds/bgm/*.ftm",
        ],
    },
    author="Airun_Iru",
)

if __name__ == "__main__":
    print("Setup script for tetr_cli package.")
