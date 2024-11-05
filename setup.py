from setuptools import setup, find_packages

setup(
    name="problem-processor",
    version="0.1",
    packages=find_packages(),
    install_requires=[
        'openai',
        'pyyaml',
        'pytest',
        'pytest-asyncio',
        'pytest-cov',
    ],
) 