import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pyttygif",
    version="0.3.1",
    author="Vitaly Ostrosablin",
    author_email="tmp6154@yandex.ru",
    description="ttyrec to GIF converter",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/tmp6154/pyttygif",
    packages=setuptools.find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Console",
        "Intended Audience :: End Users/Desktop",
        "Programming Language :: Python :: 3 :: Only",
        "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
        "Operating System :: POSIX",
        "Topic :: Multimedia :: Graphics :: Capture :: Screen Capture",
        "Topic :: Terminals :: Terminal Emulators/X Terminals",
    ],
) 
