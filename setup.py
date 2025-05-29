from setuptools import setup, find_packages

setup(
    name="FridgeFunctions",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'qcodes',
        'numpy',
        'time',
        'logging',
        'abc'
    ],
    description="A package for automating certain low-temperature measurements in CCMP, QMUL.",
    author="Owen",
    author_email="joseph.r.owen@qmul.ac.uk",
    url="https://https://github.com/jrseph/FridgeFunctions",
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ],
)
