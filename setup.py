from setuptools import setup

setup(
    name='CircuitPython_LCD',
    version='0.1.0',
    packages=['lcd'],
    url='',
    license='MIT',
    author='Fabian',
    author_email='maystar@web.de',
    description='LCD driver for  HD4480 behind PCF8574',
    install_requires=[
        'Adafruit-Blinka',
        'adafruit-circuitpython-busdevice'
    ]
)
