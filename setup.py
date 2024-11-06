from setuptools import setup, find_packages

# Load the README file for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="tusk-app",  # The name of your package
    version="0.1.0",  # Version of your package
    author="Vedant Asati",
    author_email="vedant.asati03@gmail.com",
    description="A Markdown editor app with auto-save and live preview built with Textual",
    long_description=long_description,
    long_description_content_type="text/markdown",  # Ensures markdown formatting on PyPI
    url="https://github.com/yourusername/tusk-app",  # URL to your GitHub repository
    packages=find_packages(),  # Automatically find and include packages in the tusk/ directory
    install_requires=[
        "textual",  # Add other dependencies your app requires here
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Adjust license accordingly
        "Operating System :: OS Independent",
    ],
    entry_points={
        "console_scripts": [
            "tusk=tusk.app:Tusk.run",  # This creates the 'tusk' CLI command
        ],
    },
    python_requires='>=3.7',  # Specify the minimum Python version
)
