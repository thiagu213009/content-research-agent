# Global callback system for real-time UI updates
_callback = None

def set_callback(fn):
    global _callback
    _callback = fn

def clear_callback():
    global _callback
    _callback = None

def notify(node: str, status: str, message: str = ""):
    """
    node: trends, news, statistics, examples, 
          aggregator, reflection, writer, planner, router
    status: running, done, retry, error
    message: optional detail (e.g. quality score)
    """
    if _callback:
        _callback(node, status, message)