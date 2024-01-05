import setuptools

setuptools.setup(
    name="xgit",
    packages=setuptools.find_packages(),
    install_requires=["typer>=0.9.0", "rich", "typing_extensions"],
    entry_points={"console_scripts": ["xgit = xgit.cli:main"]},
)
