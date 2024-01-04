import typer

from xgit.commands import init, cat_file, ls_files, hash_object

app = typer.Typer(add_completion=False, rich_markup_mode="markdown")


app.command()(hash_object.hash_object)
app.command()(init.init)
app.command()(cat_file.cat_file)
app.command()(ls_files.ls_files)


def main():
    app()
