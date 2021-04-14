import click
from halo import Halo
from .svm import Shop, DummyShop
from .exceptions import Failure

shop = w if (w := Shop.load(silent=True)) else DummyShop()

@click.group()
def cli():
    pass

@click.command()
def init():
    shop = Shop.init()

@click.command()
@click.option('--reason', help="The changes made in this commit", default="Made changes")
def save(reason):
    shop.save(reason)

@click.command()
@click.option('--file', help='The file to be backed up to', default='shop')
def backup(file):
    shop.backup(file)

@click.command()
@click.option('--file', help='The file to be restored from', default='shop')
@click.option('--no-catch', help='raise all errors normally', default=False, is_flag=True)
def restore(file, no_catch):
    Shop.load_from_backup(file, no_catch)

@click.command()
@click.option('--tree', help='Whether the display should be a tree', is_flag=True)
def inspect(tree):
    shop.inspect(not tree)

cli.add_command(init)
cli.add_command(save)
cli.add_command(inspect)
cli.add_command(backup)
cli.add_command(restore)

def main():
    try:
        cli()
    except Failure as e:
        spinner = e.args[1] if len(e) > 1 else Halo()
        spinner.fail(e.args[0])

if __name__ == '__main__':
    cli()
