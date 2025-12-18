# app/exceptions.py
class ValidationError(Exception):
    def __init__(self, message="Input data is invalid or missing", code="400"):
        self.message = message
        self.code = code

class DuplicateEntryError(Exception):
    def __init__(self, message="Resource already exists", code="409"):
        self.message = message
        self.code = code

class DBInsertError(Exception):
    def __init__(self, message="DB operation failed", code="500"):
        self.message = message
        self.code = code

class NotFoundError(Exception):
    def __init__(self, message="Resource not found", code="404"):
        self.message = message
        self.code = code

class DBReadError(Exception):
    def __init__(self, message="DB operation failed", code="500"):
        self.message = message
        self.code = code

class DBUpdateError(Exception):
    def __init__(self, message="DB operation failed", code="500"):
        self.message = message
        self.code = code

class DBDeleteError(Exception):
    def __init__(self, message="Resource is in use (FK constraint)", code="409"):
        self.message = message
        self.code = code

class UnknownError(Exception):
    def __init__(self, message="Unexpected error occurred", code="500"):
        self.message = message
        self.code = code
        
class AccessDeniedError(Exception):
    def __init__(self, message="Access denied", code="403"):
        self.message = message
        self.code = code