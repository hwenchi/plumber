import inspect


class Flow:
    def __init__(self, fn, inlet, outlet, poll_interval):
        self.fn = fn
        self.inlet = inlet
        self.outlet = outlet
        self.poll_interval = poll_interval
        self.arity = len(inspect.signature(fn).parameters)

    def __call__(self, drop_in, reservoir):
        if self.arity == 0:
            return self.fn(), reservoir
        elif self.arity == 1:
            return self.fn(drop_in), reservoir
        else:
            return self.fn(drop_in, reservoir)

    @property
    def id(self):
        return f"{self.fn.__module__}.{self.fn.__name__}"

    def __repr__(self):
        return self.id


def valve(inlet=None, outlet=None, poll_interval=0.1):
    def decorate(fn):
        return Flow(fn, inlet, outlet, poll_interval)

    return decorate