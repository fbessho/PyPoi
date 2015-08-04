from setuptools import setup
import os

desciption = '"Py"thon program for "Poi"sson Image Editing'
if os.path.exists('README.txt'):
    long_description = open('README.txt').read()
else:
    long_description = desciption

setup(
    name='pypoi',
    version='0.2.0',
    description=desciption,
    long_description=long_description,
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
    ],

    author='Fumihiro Bessho (Ben)',
    author_email='fumihiro.bessho@gmail.com',
    url='https://github.com/fbessho/PyPoi',
    packages=['pypoi', 'pypoi.testimages'],
    package_data={'pypoi': ['testimages/*.png']},
    scripts=['scripts/pypoi']
)
