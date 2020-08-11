from .brush import BrushThread


class Loader:
    def __init__(self, desc, **kwargs):
        self.brush = BrushThread(desc, **kwargs)

    def __enter__(self):
        self.brush.start()
        return self.brush

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.brush.stop(exc_type)
        self.brush.join()
