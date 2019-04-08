from setuptools import setup

desciption = '"Py"thon program for "Poi"sson Image Editing'
long_description = open('README.md').read()

setup(
    name='pypoi',
    version='0.3.2',
    description=desciption,
    long_description=long_description,
    long_description_content_type='text/markdown',
    license='Apache License 2.0',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Environment :: MacOS X',
        'Environment :: Win32 (MS Windows)',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
    ],

    author='Fumihiro Bessho (Ben)',
    author_email='fumihiro.bessho@gmail.com',
    url='https://github.com/fbessho/PyPoi',
    packages=['pypoi', 'pypoi.testimages'],
    package_data={'pypoi': ['testimages/*.png']},
    entry_points = {
        'console_scripts': ['pypoi=pypoi.gui:main'],
    },
    install_requires=['Pillow', 'numpy', 'pyamg', 'scipy', 'future']
)

