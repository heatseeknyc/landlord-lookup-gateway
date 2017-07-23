from functools import wraps

def wrapsafe(logger):
    """
    A dead-simple exception-handling wrapper for our internal API calls.
    The assumption is that if something slips through unchecked by this point,
    then the error message would be too confusing for the frontend users to
    make sense of it, anyway.  So instead we just log the exception, and
    let the frontend decide how to present this to the user (which will
    probably be to display some variant of "Sorry, but somethint went wrong.  
    Please try again in a little while.")
    """
    def register_function(callf,*args,**kwargs):
        def called(*args,**kwargs):
            try:
                return callf(*args,**kwargs)
            except Exception as e:
                logger.info("exception = %s" % e)
                logger.exception(e)
                return {'error':'internal error'}
        return called
    return register_function


