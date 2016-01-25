#!/usr/bin/python3

from setuptools import setup
from pip.req import parse_requirements

reqs = parse_requirements('requirements.txt')
reqs = [str(ir.req) for ir in reqs]

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
        install_requires=reqs
    )


if __name__ == "__main__":
    main()
