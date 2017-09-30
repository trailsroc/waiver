from setuptools import setup

setup(
    name='Waiver',
    packages=['Waiver'],
    include_package_data=True,
    install_requires=[
        'flask',
        'sqlite3',
        'base64',
        'fuzzywuzzy[speedup]',
        'Pillow',
        'fpdf',
    ],
)
