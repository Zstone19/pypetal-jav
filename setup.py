from setuptools import setup

NAME = 'pypetal-jav'
VERSION = '0.1.1'
URL = 'https://github.com/Zstone19/pypetal-jav'

AUTHOR = 'Zachary Stone'
EMAIL = 'stone28@illinois.edu'

#Get requirements.txt
REQUIREMENTS = []
with open('requirements.txt', 'r') as f:

    for line in f.readlines():
        REQUIREMENTS.append( line.strip('\n\r')  )




setup(
    name=NAME,
    version=VERSION,
    url='https://github.com/Zstone19/pypetal-jav',
    author=AUTHOR,
    author_email=EMAIL,
    maintainer=AUTHOR,
    maintainer_email=EMAIL,
    license='MIT',
    install_requires=REQUIREMENTS,
    python_requires='<3.0',
    packages=['pypetal_jav'],
    package_dir={'pypetal_jav':'./src/pypetal-jav'},
    include_package_data=True
)
