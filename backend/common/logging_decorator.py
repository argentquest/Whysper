import functools
import inspect
from .logger import get_logger

def log_method_call(func):
    def _log_entry(logger, func_name, args, kwargs):
        arg_reprs = [repr(a)[:200] for a in args[1:]]
        kwarg_reprs = {k: repr(v)[:200] for k, v in kwargs.items()}
        logger.debug(f"Entering {func_name} with args: {arg_reprs}, kwargs: {kwarg_reprs}")

    def _log_exit(logger, func_name, result):
        res_repr = repr(result)[:200]
        logger.info(f"Exiting {func_name} with result: {res_repr}")

    def _get_func_name(func, args):
        class_name = ""
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__
        return f"{class_name}.{func.__name__}" if class_name else func.__name__

    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            func_name = _get_func_name(func, args)
            _log_entry(logger, func_name, args, kwargs)
            try:
                result = await func(*args, **kwargs)
                _log_exit(logger, func_name, result)
                return result
            except Exception as e:
                logger.error(f"Exception in {func_name}: {e}", exc_info=True)
                raise
        return async_wrapper
    else:
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            logger = get_logger(func.__module__)
            func_name = _get_func_name(func, args)
            _log_entry(logger, func_name, args, kwargs)
            try:
                result = func(*args, **kwargs)
                _log_exit(logger, func_name, result)
                return result
            except Exception as e:
                logger.error(f"Exception in {func_name}: {e}", exc_info=True)
                raise
        return sync_wrapper
