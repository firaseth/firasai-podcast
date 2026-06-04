from setuptools import setup, find_packages

setup(
    name="firasai-podcast",
    version="0.1.0",
    packages=find_packages(),
    python_requires=">=3.9",
    install_requires=[
        "openai>=2.0.0",
        "anthropic==0.18.1",
        "requests==2.31.0",
        "python-dotenv==1.0.1",
        "schedule==1.2.1",
        "notion-client==2.0.0",
        "elevenlabs==0.2.0",
        "pydub==0.25.1",
    ],
)
