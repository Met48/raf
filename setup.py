from distutils.core import setup

setup(
    name='raf',
    packages=['raf'],
    version='0.1.0',
    url='http://github.com/Met48/raf',
    license='MIT',
    author='Andrew Sutton',
    author_email='me@andrewcsutton.com',
    description='A library for reading League of Legends raf files.',
    classifiers=[
        'Programming Language :: Python',
        'Development Status :: 2 - Pre-Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ],
    install_requires=[
        "construct>=2.5.1",
    ],
)
