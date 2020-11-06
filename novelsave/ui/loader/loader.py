from .brush import BrushThread


class Loader:
    def __init__(self, desc, draw=False, **kwargs):
        self.brush = BrushThread(desc, **kwargs)
        self.draw = draw

    def __enter__(self):
        if self.draw:
            self.brush.start()
            return self.brush
        else:
            return self.brush

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self.draw:
            self.brush.stop(exc_type)
            self.brush.join()