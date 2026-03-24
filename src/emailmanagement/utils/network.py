import asyncio
import functools
import logging
from typing import Callable, Any

def async_retry(retries: int = 3, backoff_factor: float = 2.0, initial_delay: float = 1.0):
    """
    Decorator for asynchronous functions to retry on failure with exponential backoff.
    """
    def decorator(func: Callable):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            delay = initial_delay
            last_exception = None
            
            for attempt in range(retries):
                try:
                    return await func(*args, **kwargs)
                except Exception as e:
                    last_exception = e
                    if attempt == retries - 1:
                        break
                    
                    logging.warning(f"Attempt {attempt + 1} for {func.__name__} failed: {e}. Retrying in {delay}s...")
                    await asyncio.sleep(delay)
                    delay *= backoff_factor
                    
            raise last_exception
        return wrapper
    return decorator
