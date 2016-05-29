from setuptools import setup, find_packages

setup(
    name="territory_war",
    version="1.0",
    packages=find_packages(),
    install_requires=['world>=1'],
    author="Nikolay Zhelyazkov",
    author_email="progressiven6@gmail.com",
    description="This is a package for the Territory war game.",
    license="GNU GENERAL PUBLIC LICENSE Version 2",
    keywords="tw territory war strategy turn",
    url="https://github.com/niksanaznc/territory-war-game"
)