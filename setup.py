from setuptools import setup

with open('README.md','r') as f:
    long_description = f.read()

setup(name='EventAnnotator',
      version='1.0.0',
      author='Roger Selzler',
      author_email = 'roger.selzler@carleton.ca',
      long_description = long_description,
      packages=['EventAnnotator'],
      scripts=[],
      python_requires='>=3',
      install_requires=[
          'pandas>= 1.0',
          'numpy>= 1.18',
          'matplotlib>= 3.2',
          'PyQt5',
          ])

