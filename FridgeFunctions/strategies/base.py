# -----------------------------------------------------------
# APPLY/MEASURE STRATEGY BASE CLASSES
# -----------------------------------------------------------

class ApplyStrategy(ABC):
    @abstractmethod
    def setup(self, instrument, **kwargs):
        pass

    @abstractmethod
    def apply(self, **kwargs):
        pass

    @abstractmethod
    def reset(self, **kwargs):
        pass


class MeasureStrategy(ABC):
    @abstractmethod
    def setup(self, instrument, **kwargs):
        pass

    @abstractmethod
    def measure(self, **kwargs):
        pass

    @abstractmethod
    def reset(self, **kwargs):
        pass
