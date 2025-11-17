class Namespace:
    def __init__(self, **kwargs: object) -> None:
        self.__dict__.update(kwargs)
