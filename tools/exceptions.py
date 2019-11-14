class IsNotTimeException(Exception):
    """Raised when reward date has come but current block's timestamp is less than reward date """
    pass


class NodeNotFoundException(Exception):
    """Raised when Node ID doesn't exist in SKALE Manager"""
    pass
