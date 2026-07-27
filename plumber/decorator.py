import inspect


class Flow:
    def __init__(self, fn, inlet, outlet, backoff, throttle):
        self.fn = fn
        self.inlet = inlet
        self.outlet = outlet
        self.backoff = backoff
        self.throttle = throttle
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


def valve(inlet=None, outlet=None, backoff=0.1, throttle=0.0):
    def decorate(fn):
        return Flow(fn, inlet, outlet, backoff, throttle)

    return decorate