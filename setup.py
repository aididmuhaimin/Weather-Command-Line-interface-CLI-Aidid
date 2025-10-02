"""
Setup script for Weather CLI Tool.
"""

from setuptools import setup, find_packages

setup(
    name="weather-cli-tool",
    version="1.0.0",
    author="Aidid Muhaimin Bin Mahadi",
    author_email="aidid.muhaimin011@gmail.com",
    description="A simple command-line weather application with clean text output",
    long_description=open("README.md", encoding="utf-8").read() if open("README.md").read() else "A command-line weather interface with clean text output",
    long_description_content_type="text/markdown",
    url="https://github.com/aididmuhaimin/weather-cli-tool",
    packages=find_packages(),
    python_requires=">=3.8",
    install_requires=[
        "click>=8.0.0",
        "requests>=2.25.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "pytest-mock>=3.10.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
        ],
    },
    entry_points={
        'console_scripts': [
            'weather-cli=weather_cli.cli:run_cli',
            'weather=weather_cli.cli:run_cli',
        ],
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    keywords="weather cli command-line openweathermap malaysia",
)