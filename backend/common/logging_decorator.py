import functools
import inspect
from .logger import get_logger

def log_method_call(func):
    # Helper function to log method entry with formatted args and kwargs
    def _log_entry(logger, func_name, args, kwargs):
        # Truncate args and kwargs representations to 200 chars for readability
        arg_reprs = [repr(a)[:200] for a in args[1:]]
        kwarg_reprs = {k: repr(v)[:200] for k, v in kwargs.items()}
        logger.debug(f"Entering {func_name} with args: {arg_reprs}, kwargs: {kwarg_reprs}")

    # Helper function to log method exit with result
    def _log_exit(logger, func_name, result):
        # Truncate result representation to 200 chars for readability
        res_repr = repr(result)[:200]
        logger.info(f"Exiting {func_name} with result: {res_repr}")

    # Determine the full function name, including class name if applicable
    def _get_func_name(func, args):
        # Initialize class name as empty string
        class_name = ""
        # Check if first arg is an instance with a class
        if args and hasattr(args[0], '__class__'):
            class_name = args[0].__class__.__name__
        # Return fully qualified function name
        return f"{class_name}.{func.__name__}" if class_name else func.__name__

    # Handle async functions separately
    if inspect.iscoroutinefunction(func):
        @functools.wraps(func)
        async def async_wrapper(*args, **kwargs):
            # Get logger for the function's module
            logger = get_logger(func.__module__)
            # Get full function name
            func_name = _get_func_name(func, args)
            # Log method entry
            _log_entry(logger, func_name, args, kwargs)
            try:
                # Execute async function and capture result
                result = await func(*args, **kwargs)
                # Log method exit
                _log_exit(logger, func_name, result)
                return result
            except Exception as e:
                # Log any exceptions with full traceback
                logger.error(f"Exception in {func_name}: {e}", exc_info=True)
                raise
        return async_wrapper
    else:
        # Handle synchronous functions
        @functools.wraps(func)
        def sync_wrapper(*args, **kwargs):
            # Get logger for the function's module
            logger = get_logger(func.__module__)
            # Get full function name
            func_name = _get_func_name(func, args)
            # Log method entry
            _log_entry(logger, func_name, args, kwargs)
            try:
                # Execute function and capture result
                result = func(*args, **kwargs)
                # Log method exit
                _log_exit(logger, func_name, result)
                return result
            except Exception as e:
                # Log any exceptions with full traceback
                logger.error(f"Exception in {func_name}: {e}", exc_info=True)
                raise
        return sync_wrapper
