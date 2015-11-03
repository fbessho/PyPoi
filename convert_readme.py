"""Convert README.me to rST format."""
import pypandoc
import os

if os.path.exists('README.txt'):
    print 'Removing README.txt'
    os.remove('README.txt')

output = pypandoc.convert('README.md', 'rst', outputfile='README.txt')

