from setuptools import setup

setup(
    name='Waiver',
    packages=['Waiver'],
    include_package_data=True,
    install_requires=[
        'flask',
        'Pillow',
        'fpdf',
    ],
)
