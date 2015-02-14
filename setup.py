from distutils.core import setup
setup(name='PyPoi',
      version='0.2.0',
      author='Fumihiro Bessho (Ben)',
      author_email='fumihiro.bessho@gmail.com',
      url='https://github.com/fbessho/PyPoi',
      packages=['pypoi', 'pypoi.testimages'],
      package_data={'pypoi': ['testimages/*.png']},
      scripts=['scripts/pypoi-gui']
      )

