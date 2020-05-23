from setuptools import setup

setup(
    name='SB-BigFattiesModManager',
    version='0.0.0',
    packages=[''],
    url='https://forum.weightgaming.com/',
    license='MIT',
    author='grotlover2',
    author_email='grotlover2@live.com',
    description='A mod manager for Starbound that focuses on the weight gain mods on Weightgaming',
    install_requires=['pymongo', 'pyyaml'],
    entry_points={
        'console_scripts': [
            'sb-modmanager = App:main'
        ],
    },
)
