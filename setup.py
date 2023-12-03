import setuptools

setuptools.setup(
    name="xgit",
    packages=setuptools.find_packages(),
    install_requires=["typer>=0.9.0"],
    entry_points={"console_scripts": ["xgit = xgit.cli:main"]},
)
