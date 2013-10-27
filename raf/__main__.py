"""
Usage:
  python -m raf
  python -m raf help
  ptyhon -m raf ARCHIVE
  python -m raf root PATH

Arguments:
  ARCHIVE  - Path to a .raf file. Corresponding .raf.data must be in same directory.
  PATH     - Path to a folder containing versioned subfolders with raf files.

"""

import shlex
import os
import sys

import six
import six.moves

from . import RAFArchive, RAFMaster


class RAFCLI(object):
    """
    Commands:
      help: Display this message
      open NAME PATH: Open an archive
      root NAME PATH: Open a root folder as a master archive
      use NAME: Use specific archive
      list: List open archives
      find NAME: List files with specified NAME
      re PATTERN: List files which match PATTERN
      dump PATH PATTERN: Dump files which match PATTERN into PATH.
                         Does not prompt to overwrite.
      close NAME: Close an archive
      quit: Exit interactive prompt.
    """
    COMMANDS = {
        ('h', 'help'): 'help',
        ('o', 'open'): 'open_archive',
        ('root',): 'open_root',
        ('u', 'use'): 'use',
        ('l', 'list'): 'list',
        ('f', 'find'): 'find',
        ('re',): 'find_re',
        ('d', 'dump'): 'dump',
        ('c', 'close'): 'close',
    }

    def __init__(self):
        self._archives = {}
        self._masters = {}
        self._index = {}
        self._active_archive = None

    def open_archive(self, name, path):
        if name in self._index:
            raise RuntimeError("Archive with name already open.")
        archive = RAFArchive(path)
        self._archives[name] = archive
        self._index[name] = archive
        print("Opened archive.")
        return archive

    def open_root(self, name, path):
        if name in self._index:
            raise RuntimeError("Archive with name already open.")
        archive = RAFMaster(path)
        self._masters[name] = archive
        self._index[name] = archive
        print("Opened archive.")
        return archive

    def use(self, name):
        if name not in self._index:
            raise RuntimeError("No archive opened with that name.")
        self._active_archive = self._index[name]
        print("Using archive %s." % name)

    def close(self, name):
        if name not in self._index:
            raise RuntimeError("No archive opened with that name.")
        archive = self._index[name]
        if name in self._archives:
            del self._archives[name]
        if name in self._masters:
            del self._masters[name]
        if self._active_archive == archive:
            self._active_archive = None
        del self._index[name]
        print("Closed %s." % name)

    def list(self):
        print('\n'.join(self._index.keys()))

    def dump(self, output_path, pattern):
        if self._active_archive is None:
            raise RuntimeError("No archive is active.")
        entries = self._active_archive.find_re(pattern)
        for entry in entries:
            path = os.path.join(output_path, entry.path)
            directory = os.path.dirname(path)
            print('Write file: %s' % path)
            try:
                os.makedirs(directory)
            except Exception:
                pass
            with open(path, 'wb') as f:
                f.write(entry.read())

    def find(self, name):
        if self._active_archive is None:
            raise RuntimeError("No archive is active.")
        res = self._active_archive.find(name=name)
        print('\n'.join('\n  '.join((x.fh._path, x.path)) for x in res))

    def find_re(self, pattern):
        if self._active_archive is None:
            raise RuntimeError("No archive is active.")
        res = self._active_archive.find_re(pattern)
        print('\n'.join('\n  '.join((x.fh._path, x.path)) for x in res))

    def help(self):
        print(self.__class__.__doc__)

    def repl(self):
        while True:
            input = six.moves.input('> ')
            input = shlex.split(input)
            command = input[0]
            if command == 'quit':
                break
            for available_command in self.COMMANDS:
                if command in available_command:
                    method_name = self.COMMANDS[available_command]
                    method = getattr(self, method_name)
                    arg_count = six.get_function_code(method).co_argcount
                    if len(input) != arg_count:
                        print("Wrong argument count.")
                        print("Expected %s" % arg_count)
                        break
                    try:
                        result = method(*input[1:])
                    except Exception as e:
                        print(e)
                    else:
                        if result is not None:
                            print(result)
                    break
            else:
                print("Invalid command.")


def main(args):
    if len(args) > 2:
        print("Too many arguments.")
        print(__doc__)
        sys.exit(1)

    cli = RAFCLI()

    if len(args) == 1:
        cli.open_archive('default', args[0])
        cli.use('default')
    elif len(args) == 2:
        assert args[0].lower() == 'root'
        cli.open_root('default', args[1])
        cli.use('default')

    cli.repl()

main(sys.argv[1:])