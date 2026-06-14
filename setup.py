from setuptools import setup, find_packages

setup(
    name="firasai-podcast",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "openai>=2.0.0",
        "requests>=2.31.0",
        "python-dotenv>=1.0.1",
        "schedule>=1.2.1",
    ],
)
