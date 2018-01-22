#!/usr/bin/python3

from setuptools import setup
from pip.req import parse_requirements

def main():
    setup(
        name='craftbuildtools',
        version='0.0.1',
        packages=[
            'craftbuildtools'
        ],
        url='https://github.com/TechnicalBro/CraftBuildTools',
        license='LICENSE.txt',
        author='Brandon Curtis',
        author_email='freebird.brandon@gmail.com',
        description='Build automation and Project creation for Minecraft/Spigot/Bukkit, Maven Projects',
        entry_points={
            'console_scripts': [
                'craftbuildtools = craftbuildtools.__main__:main'
            ]
        },
        keywords=[
            "minecraft", "spigot", "bukkit", "templates", "buildtools", "craftbuildtools"
        ],
        install_requires=[
            "beautifulsoup4==4.4.1",
            "argparse==1.4.0",
            "ftpretty==0.2.2",
            "pyyaml==3.11",
            "lxml==3.5.0",
            "cssselect==0.9.1",
            "cookiecutter==1.3.0",
            "click==6.2",
            "sh==1.11"
        ]
    )


if __name__ == "__main__":
    main()
