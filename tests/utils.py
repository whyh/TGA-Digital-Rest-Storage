import asyncio
import functools
import random
from time import time
from typing import Any, Callable, Coroutine, Tuple

OriginalOutput = Any


def timed(function: Callable[..., OriginalOutput]) -> Callable[..., Tuple[OriginalOutput, float]]:
    """
    Extends function to return it's execution time
    """

    @functools.wraps(function)
    def wrapped_function(*args: Any, **kwargs: Any) -> Tuple[OriginalOutput, float]:
        """
        :returns: Tuple of the original function output and it's execution time
        """
        now_epoch = time()
        return function(*args, **kwargs), time() - now_epoch

    return wrapped_function


AnyCoroutine = Coroutine[Any, OriginalOutput, Any]


def sync(function: Callable[..., AnyCoroutine]) -> Callable[..., OriginalOutput]:
    """
    Executes async function synchronously
    """

    @functools.wraps(function)
    def wrapped_function(*args: Any, **kwargs: Any) -> OriginalOutput:
        """
        :returns: Output of the original coroutine
        """
        return asyncio.get_event_loop().run_until_complete(function(*args, **kwargs))

    return wrapped_function


def get_random_string(length: int, *, characters: str = "1234567890QWERTYUIOPASDFGHJKLZXCVBNM") -> str:
    # For the sake of simplicity used only alpha numeric characters, that don't require to be url encoded
    assert length > 0
    return "".join(random.choice(characters) for _ in range(length))
