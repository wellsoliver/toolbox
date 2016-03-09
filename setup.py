from distutils.core import setup


version = __import__('toolbox').__version__


setup(
    name='toolbox',
    version=version,
    description='big python toolbox',
    author='Wells Oliver',
    author_email='wells.oliver@gmail.com',
    url='https://www.python.org/sigs/distutils-sig/',
    packages=[ 'toolbox' ],
 )