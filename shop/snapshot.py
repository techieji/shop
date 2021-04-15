from pathlib import Path
import pickle
import zlib
from .exceptions import Failure
from halo import Halo

class File:
    def __init__(self, filename):
        self.name = filename.as_posix()
        with open(filename, 'rb') as f:
            self.compressed = zlib.compress(f.read())

    def __str__(self): return f"File('{self.name}')"
    def __repr__(self): return f"File('{self.name}')"

    @property
    def text(self):
        return zlib.decompress(self.compressed)

    def restore(self):
        with open(self.name, 'wb') as f:
            f.write(self.text)

class Snapshot:
    def __init__(self, _path):
        path = Path(_path)
        self.files = [File(x) for x in path.iterdir() if not x.is_dir() and x.name[0] != '.']
        self.dirs  = [Snapshot(x) for x in path.iterdir() if x.is_dir() and x.name[0] != '.']
        self.name = path.as_posix()

    def __repr__(self): return f"Snapshot('{self.name}')"
    def __str__(self): return f"Snapshot('{self.name}')"
    def __rich__(self): return f"Snapshot('{self.name}')"

    def compress(self):
        dumped = pickle.dumps(self)
        return zlib.compress(dumped)

    def restore(self, spinner=None, catch=True):
        try:
            if spinner is not None: 
                spinner.start('Erasing current directory')
                for x in Path('.').iterdir():
                    try: 
                        if x.name[0] != '.': x.unlink()
                    except PermissionError: Halo().warn(f'{x} could not be deleted')
                spinner.succeed('Current directory cleaned!')
            try: (Path('.') / Path(self.name)).mkdir()
            except FileExistsError: pass
            if spinner is not None: 
                spinner.start('Restoring files')
            for x in self.files:
                x.restore()
            if spinner is not None:
                spinner.succeed('Files restored!')
                spinner.start('Restoring directories')
            for x in self.dirs:
                x.restore()
            if spinner is not None: spinner.succeed('Directories restored!')
        except:
            if not catch:
                raise
            else:
                raise Failure('Something went wrong. This is probably a bug.', spinner)

    @classmethod
    def decompress(klass, b_snap, checksum=None):
        uncompressed = zlib.decompress(b_snap)
        return pickle.loads(uncompressed)
