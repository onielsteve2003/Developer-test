class ProcessingError(Exception):
    """Exception raised for errors during processing."""
    pass

class ConfigurationError(Exception):
    """Exception raised for configuration-related errors."""
    pass

class MutationError(Exception):
    """Exception raised for errors during mutation."""
    pass

class ResourceError(Exception):
    """Exception raised for resource-related errors."""
    pass

class ValidationError(Exception):
    """Exception raised for validation errors."""
    pass 