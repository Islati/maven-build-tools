#!/usr/bin/env python
# -*- coding: utf-8 -*-

from setuptools import setup
import re

version = re.search(
    '^__version__\s*=\s*"(.*)"',
    open('craftbuildtools/bootstrap.py').read(),
    re.M
).group(1)


def main():
    setup(
        name='craftbuildtools',
        version=version,
        packages=[
            'craftbuildtools',
            'craftbuildtools.data',
            'craftbuildtools.operations',
            'craftbuildtools.template',
            'craftbuildtools.utils'
        ],
        url='https://github.com/TechnicalBro/CraftBuildTools',
        license='LICENSE.txt',
        author='Brandon Curtis',
        author_email='freebird.brandon@gmail.com',
        description='Build automation and Project creation for Minecraft/Spigot/Bukkit, Maven Projects',
        entry_points={
            'console_scripts': [
                'craftbuildtools = craftbuildtools.bootstrap:main'
            ]
        },
        keywords=[
            "minecraft", "spigot", "bukkit", "templates", "buildtools", "craftbuildtools"
        ],
        install_requires=[
            'beautifulsoup4==4.4.1',
            'argparse==1.4.0',
            'ftpretty==0.2.2',
            'pyyaml==3.11',
            'requests',
            'lxml==4.9.1',
            'cssselect==0.9.1',
            'cookiecutter==1.3.0',
            'click==6.2',
            'sh==1.11',
            'simpleplugins==0.1.2',
            'yamlbro',
            'argparse',
        ],
        dependency_links=[
            'git+https://github.com/TechnicalBro/yaml-bro.git',
            'git+https://github.com/TechnicalBro/simple-python-plugins.git'
        ],
        test_suite='tests',
        tests_require=[
            'py',
            'pytest',
            'pytest-cov',
            'pytest-random'
        ],
        classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Intended Audience :: Developers',
            'Intended Audience :: System Administrators',
            'Natural Language :: English',
            'License :: OSI Approved :: MIT License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Programming Language :: Python :: 3.3',
            'Programming Language :: Python :: 3.4'
        ],
    )


if __name__ == "__main__":
    main()
