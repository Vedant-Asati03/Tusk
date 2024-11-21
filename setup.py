from setuptools import setup, find_packages

setup(
    name="tusk-editor",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "textual>=0.79.1",
        "Markdown>=3.7",
        "pypandoc>=1.14",
        "GitPython>=3.1.40",
    ],
    entry_points={
        'console_scripts': [
            'tusk=tusk.cli:main',
        ],
    },
    author="vedant-asati03",
    author_email="vedant.asati03@gmail.com",
    description="A modern terminal-based Markdown editor with Git integration",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    url="https://github.com/vedant-asati03/tusk",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.10",
)
