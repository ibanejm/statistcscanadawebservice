from setuptools import setup, find_packages

setup(
    name="statcan-webservice",
    version="0.1.0",
    description="A Python service to retrieve public data from Statistics Canada Web Data Service",
    author="Statistics Canada Web Service",
    packages=find_packages(),
    install_requires=[
        "requests>=2.31.0",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
