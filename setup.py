import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()

with open("requirements.txt", "r") as f:
    dependencies = [line.rstrip() for line in f]

setuptools.setup(
    name="WDR3 Concert Downloader",
    version="2.7.0",
    author="Dr. Ralf Antonius Timmermann",
    author_email="rtimmermann@gmx.de",
    description="Download appropriate mp3 to file, where's no download button",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Tamburasca/WDR3_concert_downloader",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: BSD 3-Clause",
        "Operating System :: OS Independent",
    ],
    python_requires='=3.12',
    install_requires=dependencies,
    license='BSD 3-Clause',
)