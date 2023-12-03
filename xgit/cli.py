import typer

app = typer.Typer(add_completion=False)

@app.command()
def init():
    print("Hello World")

@app.command()
def commit():
    print("Hello World")

def main():
    app()
