"""
Exceptions for the Greyscale Binary Separator module.
"""


class GreyscaleBinarySeparatorError(Exception):
    """Base exception for all Greyscale Binary Separator errors."""

    pass


class RegionDetectionError(GreyscaleBinarySeparatorError):
    """Error during region detection."""

    pass


class RegionProcessingError(GreyscaleBinarySeparatorError):
    """Error during region processing."""

    pass


class ConfigurationError(GreyscaleBinarySeparatorError):
    """Error in configuration parameters."""

    pass
