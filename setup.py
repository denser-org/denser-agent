from setuptools import setup, find_packages

setup(
    name="denser_agent",
    version="0.1.0",
    packages=["agents", "tools"],
    python_requires=">=3.7",
    install_requires=[
        # Add your dependencies here, e.g.:
        # "requests>=2.25.0",
        # "numpy>=1.20.0",
    ],
    author="Denser",
    author_email="support@denser.ai",
    description="A multi-agent system built on MCP (Model Context Protocol) architecture",
    long_description=open("README.md").read() if open("README.md") else "",
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/denser-agent",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)