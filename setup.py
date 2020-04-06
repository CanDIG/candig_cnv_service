import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="candig-cnv-service", # Replace with your own username
    version="0.0.1",
    author="Felipe Coral-Sassol",
    author_email="fcoralsasso@bcgsc.ca",
    description="Implementation of Copy-number variation",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/CanDIG/candig_cnv_service",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Natural Language :: English",        
    ],
    python_requires='>=3.6',
)
