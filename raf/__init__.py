"""
Python implementation of RAF file format.
"""

import os
import re
import zlib

from .formats import RAF_INDEX
from .util import LazyFile


class RAFEntry(object):
    """
    Lazy entry.
    """

    def __init__(self, fh, path, offset, size):
        self.path = path
        self.offset = offset
        self.size = size
        self.fh = fh
        self._data = None

    def read(self):
        if self._data is None:
            fh = self.fh.get_handle()
            fh.seek(self.offset)
            data = fh.read(self.size)
            data = zlib.decompress(data)
            self._data = data
        return self._data

    def __repr__(self):
        return '%s(%r, %r, %r, %r)' % (self.__class__.__name__,
                                      self.path,
                                      self.fh,
                                      self.offset,
                                      self.size,
        )


class RAFArchive(object):
    """
    Read-only RAF archive.
    """

    def __init__(self, path):
        print "Open archive:", path
        self.path = path
        self.entries_full = {}
        self.entries_name = {}
        with open(path, 'rb') as f:
            self.index = RAF_INDEX.parse_stream(f)
        self._data_handle = LazyFile(path + '.dat', 'rb')
        self._fill_entries()

    def _fill_entries(self):
        """Populate entries dictionaries from index."""
        for file in self.index.files:
            path = self.index.paths[file.pathIndex]
            data_offset = file.dataOffset
            data_size = file.dataSize
            obj = RAFEntry(self._data_handle, path, data_offset, data_size)
            # Add to full path dictionary
            assert path not in self.entries_full
            self.entries_full[path.lower()] = obj
            # Add to name dictionary
            name = os.path.basename(path).lower()
            if name not in self.entries_name:
                self.entries_name[name] = []
            self.entries_name[name].append(obj)

    def entries_by_path(self):
        return self.entries_full

    def entries_by_name(self):
        return self.entries_name

    def find(self, path=None, name=None):
        if path is None and name is None:
            # TODO: Correct error type
            raise ValueError("Path or name is required.")
        if path:
            return self.entries_full[path.lower()]
        else:
            # TODO: Return multiple?
            return self.entries_name[name.lower()][-1]

    def find_re(self, pattern):
        """Find all entries whose path matches a given pattern."""
        pattern = re.compile(pattern)
        for k, v in self.entries_by_path().iteritems():
            if pattern.search(k):
                yield v

    def read(self, path=None, name=None):
        return self.find(path=path, name=name).read()


class RAFMaster(object):
    """
    Groups all RAF files, as if there is one archive.

    """

    def __init__(self, base_path):
        self.entries_full = {}
        self.entries_name = {}
        paths = self._get_archive_paths(base_path)
        paths = list(paths)
        self.archives = [RAFArchive(path) for path in paths]
        self._fill_entries()

    @staticmethod
    def _get_archive_paths(base_path):
        # Each directory name is a version number
        # A version number is 4 dot-separated integers
        version_sorter = lambda (_dir, _): map(int, _dir.split('.'))
        directories = os.listdir(base_path)
        directories = ((d, os.path.join(base_path, d)) for d in directories)
        directories = [(d, f) for d, f in directories if os.path.isdir(f)]
        directories.sort(key=version_sorter)
        # Need to find the .raf file in the folder
        for _, directory in directories:
            files = os.listdir(directory)
            files = (os.path.join(directory, f) for f in files)
            files = filter(os.path.isfile, files)
            files = (f for f in files if re.search(r"(?i)\.raf$", f))
            yield next(files)
            #return directories

    def _fill_entries(self):
        # Archives are sorted, so last entry will always be most recent file
        for archive in self.archives:
            # TODO: Reduce code duplication
            by_path = archive.entries_by_path()
            for path, entry in by_path.items():
                if path not in self.entries_full:
                    self.entries_full[path] = []
                self.entries_full[path].append(entry)
            by_name = archive.entries_by_name()
            for name, entry in by_name.items():
                if name not in self.entries_name:
                    self.entries_name[name] = []
                self.entries_name[name].append(entry)

    def find(self, path=None, name=None):
        """
        Returns most recent version of the matching file.
        If there are multiple files of the same name and version, a random one is used.

        """
        if path is None and name is None:
            # TODO: Correct error type
            raise ValueError("Path or name is required.")
            # Entries are sorted by version number, so the last will be the most recent
        # TODO: Reduce redundancy with RAFArchive
        if path:
            return self.entries_full[path.lower()][-1]
        else:
            return self.entries_name[name.lower()][-1][-1]

    def find_re(self, pattern):
        """Find the most recent versions of all entries whose path matches a given pattern."""
        # TODO: Reduce redundancy with RAFArchive
        pattern = re.compile(pattern)
        for k, v in self.entries_full.iteritems():
            if pattern.search(k):
                # Most recent version will be last
                yield v[-1]

    def read(self, path=None, name=None):
        return self.find(path=path, name=name).read()
