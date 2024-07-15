from importlib.metadata import version
import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning)
__version__ = version('jwstdestripe')
__all__ = ['destripe','__version__']
