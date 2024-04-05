"""
pifcap deticated image format
"""

import pickle

class Image:
    def __init__(self, array=None, metadata=None, format=None, comment=None):
        self.array = array
        self.metadata = metadata
        self.format =format
        self.comment = comment


    def get(self):
        Img = {
            "array": self.array,
            "format": self.format,
            "metadata": self.metadata,
            "comment": self.comment
        }
        return Img

    def estimate_FileSize(self):
        return len(pickle.dumps(self.get()))
    
    def save(self, filename):
        with open(filename, "wb") as fh:
            pickle.dump(self.get(), fh)
