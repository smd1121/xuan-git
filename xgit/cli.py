import typer

from xgit.commands import init, cat_file, ls_files, show_index, hash_object, update_index

app = typer.Typer(add_completion=False, rich_markup_mode="markdown")


app.command()(hash_object.hash_object)
app.command()(init.init)
app.command()(cat_file.cat_file)
app.command()(ls_files.ls_files)
app.command()(update_index.update_index)

app.command(hidden=True)(show_index.show_index)


def main():
    app()
