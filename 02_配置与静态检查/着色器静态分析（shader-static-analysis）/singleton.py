from typing import Any

# singleton metaclass
class Singleton(type):
    __instances = {}
    def __call__(cls, *args: Any, **kwds: Any) -> Any:
        if cls not in cls.__instances:
            cls.__instances[cls] = super(Singleton, cls).__call__(*args, **kwds)
        return cls.__instances[cls]
    