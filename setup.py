import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="orthotile",
    version="0.1.2",
    author="Abhishek Singh Thakur",
    author_email="abhi.una12@gmail.com",
    description="A python library for generating tiles of given dimensions from a original orthomosaic TIFF image.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/abhiTronix/Orthotile",
    packages=setuptools.find_packages(),
    python_requires=">=3.5",
    install_requires=[
        "gdal",
        "numpy",
        "Pillow",
        "cython",
    ],
    classifiers=[
        "Programming Language :: Python",
        "License :: OSI Approved :: Apache-2.0 license",
        "Operating System :: OS Independent",
    ],
)
