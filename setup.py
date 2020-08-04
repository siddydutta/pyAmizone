from setuptools import setup

with open("README.md", "r") as fh:
	long_description = fh.read()

setup(
	name='pyAmizone',
	version='0.0.1',
	url='https://github.com/siddharthapdutta/pyAmizone',
	author='Siddhartha Dutta',
	author_email='siddhartha.dutta1@student.amity.edu'
	description='Python Package for Amizone',
	long_description=long_description,
	long_description_content_type="text/markdown",
	py_modules=["pyAmizone"],
	package_dir={'': 'src'},
	classifiers=[
		"Development Status :: 3 - Alpha",
		"Programming Language :: Python :: 3",
		"Programming Language :: Python :: 3.7",
		"License :: OSI Approved :: MIT License",
		"Operating System :: OS Independent",
	],
    install_requires = [
        "beautifulsoup4 ~= 4.9.1",
        "requests ~= 2.24.0",
    ],
)