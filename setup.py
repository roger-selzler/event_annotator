from setuptools import setup

with open('README.md','r') as f:
    long_description = f.read()

setup(name='event_annotator',
      version='1.0.0',
      author='Roger Selzler',
      author_email = 'roger.selzler@carleton.ca',
      long_description = long_description,
      packages=['event_annotator'],
      scripts=[],
      python_requires='>=3.6',
      install_requires=[
          'pandas>=1.0',
          'numpy>=1.18',
          'matplotlib>=3.2',
          ],
      package_data={
          'ecg': ['ecg_data.csv']},
      include_package_data=True, 
      )

