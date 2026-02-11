from setuptools import setup

setup(
    name="origin-miner",
    version="0.1.0",
    py_modules=["miner"],
    install_requires=[
        "GitPython",
        "rich",
    ],
    entry_points={
        "console_scripts": [
            "miner-audit=miner:audit_repository",
        ],
    },
)
