import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pygrouper",
    version="1.0.4",
    author="OSU-IAM",
    description="Python module for working with Grouper",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/OSU-IAM/pygrouper",
    packages=setuptools.find_packages(),
    install_requires=[
        'requests'
    ],
    classifiers=[
        "Programming Language :: Python :: 3"
    ]
)
