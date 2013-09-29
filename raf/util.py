class LazyFile(object):
    def __init__(self, path, mode='r'):
        self._path = path
        self._mode = mode
        self._handle = None

    def get_handle(self):
        if self._handle is None:
            print "Open file:", self._path
            self._handle = open(self._path, self._mode)
        return self._handle

    def __del__(self):
        try:
            self._handle.close()
        except (AttributeError, IOError):
            pass

    def __repr__(self):
        return '%s(%r, %r)' % (self.__class__.__name__,
                               self._path, self._mode)
