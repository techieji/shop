from pathlib import Path
from .snapshot import Snapshot
from .exceptions import Failure
from halo import Halo
from rich import print
from rich.table import Table
from rich.tree import Tree
from rich.text import Text
from datetime import datetime
from PyInquirer import prompt
import shutil
import pickle

class Shop:
    def __init__(self, snapshots, reasons, time):
        self.snapshots = snapshots
        self.reasons = reasons
        self.time = time
        self.i = len(snapshots)
        self._l = len(snapshots)

    def debug(self):
        print(self.__dict__)

    def save(self, reason=None):
        if reason is None:
            reason = prompt([{'type': 'input', 'name': 'commit_msg', 'message': 'Please enter a commit message'}])
        with Halo(text='Saving', spinner='dots') as sp:
            self.snapshots.append(Snapshot('.'))
            self.reasons.append(reason)
            self.time.append(datetime.now())
            self._l += 1
            self.i = self._l - 1
            self.save_to_fs()
            sp.succeed('Saved a snapshot!')

    def inspect(self, table=False):
        if table:
            table = Table(title='History of this Repository')
            table.add_column('Date', style='cyan')
            table.add_column('Changes', style='magenta')
            for x, *y in zip(self.time, self.reasons):
                table.add_row(str(x), *y)
            print(table)
        else:
            current = Tree('Root')
            for x in self.reasons:
                current = current.add(x)
            print(current)

    def backup(self, filename='shop'):
        if Path(filename).exists():
            answers = prompt([{'type': 'confirm', 'name': 'overwrite', 'message': f'{filename} already exists. Do you want to overwrite it?', 'default': False}])
            if answers['overwrite']:
                pass
            else:
                Halo().info('Action not performed')
                return
        if not Path('.shop').exists():
            raise Failure('.shop does not exist. Is this running in a shop repository?')
        else:
            with Halo(text='Copying config', spinner='dots') as sp:
                shutil.copy('.shop', filename)
                sp.succeed(f'A copy of .shop is now in {filename}')

    def save_to_fs(self):
        with open('.shop', 'wb') as f:
            pickle.dump(self, f)

    def change_place(self, n):
        spinner = Halo('Updating internal state').start()
        self.i += n
        spinner.succeed('Internal state updated').start('Loading snapshot')
        self.snapshots[self.i].restore(spinner)
        self.save_to_fs()
        spinner.succeed('Snapshot loaded!')

    def revert(self, n=1):
        self.change_place(-n)

    def advance(self, n=1):
        self.change_place(n)

    @classmethod
    def load_from_backup(klass, backup='shop', catch=True, snapshot_n=-1):
        answers = prompt([{'type': 'confirm', 'name': 'overwrite', 'message': f'Any files already in this directory will be overwritten. Is that all right?', 'default': False}])
        if not answers['overwrite']: return
        spinner = Halo('Loading snapshot').start()
        klass.load(backup, catch).snapshots[snapshot_n].restore(spinner)
        spinner.start().succeed('Snapshot loaded!')

    @classmethod
    def init(klass):
        with Halo(text='Making shop repository', spinner='dots') as sp:
            s = Shop([], [], [])
            try:
                with open('.shop', 'xb') as f:
                    pickle.dump(s, f)
            except FileExistsError:
                raise Failure('Already a shop repo. You can already work in this folder!')
            else:
                sp.succeed('Created shop repo!')
                return s

    @classmethod
    def load(klass, filename='.shop', silent=False):
        try: 
            with open(filename, 'rb') as f:
                return pickle.load(f)
        except FileNotFoundError:
            if not silent:
                raise Failure("Is this is a shop repo?")

    @classmethod
    def setup(klass):
        if '.shop' in Path('.').iterdir():
            with open('.shop', 'rb') as f:
                return pickle.load(f)
        else:
            return Shop.init()

class DummyShop:
    def __getattr__(self, val):
        Halo().fail("Is this a shop repo?")
        return self
    def __call__(self, *args, **kwargs): pass
