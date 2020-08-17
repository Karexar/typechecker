import setuptools

setuptools.setup(
    name="typechecker",
    version="0.0.1",
    author="Mike Bardet",
    author_email="mikebardet4@hotmail.com",
    description="Check python types at runtime",
    license='Apache License 2.0',
    long_description="Uses decorators on functions and method to check the arguments types and return type at runtime. ",
    url="https://github.com/Karexar/typechecker",

    packages=setuptools.find_packages(),

    classifiers=(
        "Programming Language :: Python :: 3.7",
        "License :: Creative Commons (CC BY-NC 4.0)",
        "Operating System :: OS Independent",
    ),
    install_requires=[]
)
