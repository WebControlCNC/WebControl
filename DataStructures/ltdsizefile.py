import os.path

class LtdSizeFile():
    verbose = False
    ''' A file subclass which  limits size of file written to approximately "maxsize" bytes '''
    def __init__(self, filename, mode='wt', maxsize=None):
        self.root, self.ext = os.path.splitext(filename)
        self.num = 1
        self.size = 0
        if maxsize is not None and maxsize < 1:
            raise ValueError('"maxsize: argument should be a positive number')
        self.maxsize = maxsize
        file.__init__(self, self._getfilename(), mode)
        if verbose: print ('file "%s" opened' % self._getfilename())

    def close(self):
        file.close(self)
        self.size = 0
        if verbose: print ('file "%s" closed' % self._getfilename())

    def write(self, text):
        lentext =len(text)
        if self.maxsize is None or self.size+lentext <= self.maxsize:
            file.write(self, text)
            self.size += lentext
        else:
            self.close()
            self.num += 1
            file.__init__(self, self._getfilename(), self.mode)
            if verbose: print ('file "%s" opened' % self._getfilename())
            self.num += 1
            file.write(self, text)
            self.size += lentext

    def writelines(self, lines):
        for line in lines:
            self.write(line)

    def _getfilename(self):
        return '{0}{1}{2}'.format(self.root, self.num if self.num > 1 else '', self.ext)
