# custom errors

class NotARepositoryError(Exception):
    """Raise when a .pygit folder cannot be found in a path"""
    def __init__(self, message="the path is not valid") -> None:
        super().__init__(message)
