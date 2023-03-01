import setuptools

with open('README.md') as file:
    read_me_description = file.read()

with open('requirements.txt') as file:
    install_requires = file.read().split()

setuptools.setup(
    name='tool_webdata2esp',
    version='0.1.1',
    author='Polyakov Konstantin',
    author_email='shyzik93@mail.ru',
    description='The package for preparing web data for loading into ESP8266',
    long_description=read_me_description,
    long_description_content_type='text/markdown',
    url='https://github.com/syeysk/tool_webdata2esp',
    packages=['tool_webdata2esp'],
    classifiers=[
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: LGPL-3.0 License',
        'Operating System :: OS Independent',
    ],
    install_requires=install_requires,
    python_requires='>=3.6',
)