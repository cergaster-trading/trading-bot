# indicators/strategy_base.py

class StrategyFactory:
    _registry = {}

    @classmethod
    def register(cls, name, backtest_cls=None, param_space=None):
        cls._registry[name] = {
            "backtest_cls": backtest_cls,
            "param_space": param_space or {}
        }

    @classmethod
    def get(cls, name):
        return cls._registry.get(name)

    @classmethod
    def get_all(cls):
        return cls._registry


class StrategyBase:
    def __init__(self, df, **params):
        self.df = df.copy()
        self.params = params
        self.name = self.__class__.__name__

    def generate_signals(self):
        raise NotImplementedError("Each strategy must implement the generate_signals() method.")
