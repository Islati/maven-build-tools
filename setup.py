from distutils.core import setup

from pip.req import parse_requirements

reqs = parse_requirements('requirements.txt')
reqs = [str(ir.iq) for ir in reqs]

setup(
    name='CraftBuildTools',
    version='0.0.1-ALPHA',
    packages=[
        'craft_tools'
    ],
    url='',
    license='',
    author='Brandon Curtis',
    author_email='bcurtis@artectis.com',
    description='Minecraft Build tools for projects',
    install_requirements = reqs
)
