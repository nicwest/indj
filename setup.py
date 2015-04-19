from setuptools import setup

try:
    long_description = open("README.md").read()
except IOError:
    long_description = ""

setup(
    name="indj",
    version="0.1.0",
    description="A command line tool for looking up django object locations.",
    license="MIT",
    author="Nic West",
    packages=['indj'],
    package_data={'indj': ['data/*.json']},
    install_requires=['jedi==0.8.1'],
    long_description=long_description,
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.4",
    ],
    entry_points={
        'console_scripts': [
            'indj = indj.main:main'
        ]
    }
)
