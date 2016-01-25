"""bitcalc :: setup.py

Author: Christopher Rink (chrisrink10 at gmail dot com)"""
try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

setup(
    name='bitcalc',
    version='v0.1',
    packages=['bitcalc'],
    entry_points={
        "console_scripts": ['bitcalc = bitcalc.bitcalc:start_repl']
    },
    url='https://github.com/chrisrink10/bitcalc',
    license='MIT License',
    author='Christopher Rink',
    author_email='chrisrink10@gmail.com',
    description='Visual calculator for bitwise expressions'
)
