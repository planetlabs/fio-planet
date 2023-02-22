"""Fio-planet exceptions."""


class PlanetError(Exception):
    """Base class for fio-planet exceptions."""


class ReduceError(PlanetError):
    """Raised when an expression does not reduce to a single object."""
