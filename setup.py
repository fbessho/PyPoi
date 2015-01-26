from distutils.core import setup
setup(name='PyPoi',
      version='0.2.0',
      author='author',
      author_email='fumihiro.bessho@gmail.com',
      packages=['pypoi', 'pypoi.testimages'],
      package_data={'pypoi': ['testimages/*.png']},
      scripts=['scripts/pypoi-gui']
      )

