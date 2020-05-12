import setuptools
from neurodatablock import VERSION_STR

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='neurodatablock',
    version=VERSION_STR,
    description='a reference Python implementation for the `neurodatablock` data format.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url='https://github.com/gwappa/python-neurodatablock',
    author='Keisuke Sehara',
    author_email='keisuke.sehara@gmail.com',
    license='MIT',
    install_requires=[],
    python_requires='>=3.4',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        ],
    packages=setuptools.find_packages(),
    entry_points={
        'console_scripts': [
            # '%module% =%module%.__main__:run'
        ]
    }
)
