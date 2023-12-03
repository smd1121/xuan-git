import typer

from xgit.commands import init

app = typer.Typer(add_completion=False)

app.command()(init.init)


@app.command()
def commit():
    print("Hello World")


def main():
    app()
