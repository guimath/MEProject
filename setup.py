import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="MEP-gm",
    version="0.1.3",
    author="Guimath",
    author_email="guilhem.mathieux.pro@gmail.com",
    description="A program with simple GUI to help you manage music files",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/guimath/MEProject",
    project_urls={
        "Bug Tracker": "https://github.com/guimath/MEProject/issues",
    },
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: unlicense",
        "Operating System :: OS Independent",
    ],
    package_dir={"": "mep"},
    packages=setuptools.find_packages(where="mep"),
    python_requires=">=3.6",
)