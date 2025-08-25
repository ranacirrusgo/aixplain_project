"""
Setup script for Policy Navigator Agent
"""

from setuptools import setup, find_packages
from pathlib import Path

# Read README for long description
readme_path = Path(__file__).parent / "README.md"
long_description = readme_path.read_text(encoding="utf-8") if readme_path.exists() else ""

# Read requirements
requirements_path = Path(__file__).parent / "requirements.txt"
requirements = []
if requirements_path.exists():
    with open(requirements_path, 'r') as f:
        requirements = [line.strip() for line in f if line.strip() and not line.startswith('#')]

setup(
    name="policy-navigator-agent",
    version="1.0.0",
    author="Policy Navigator Team",
    author_email="dev@policynavigator.ai",
    description="A Multi-Agent RAG System for Government Regulation Search",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/policy-navigator-agent",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Legal Industry",
        "Intended Audience :: Government",
        "Topic :: Office/Business :: Legal",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.8",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
        "docs": [
            "sphinx>=5.0.0",
            "sphinx-rtd-theme>=1.0.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "policy-navigator=cli:cli",
        ],
    },
    include_package_data=True,
    package_data={
        "": ["*.md", "*.txt", "*.yml", "*.yaml"],
    },
    keywords="ai, legal, government, regulations, compliance, rag, agents",
    project_urls={
        "Bug Reports": "https://github.com/yourusername/policy-navigator-agent/issues",
        "Source": "https://github.com/yourusername/policy-navigator-agent",
        "Documentation": "https://policy-navigator-agent.readthedocs.io/",
    },
)