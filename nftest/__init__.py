"""NFTest module."""

try:
    from nftest._version import version as __version__  # noqa: F401
except ModuleNotFoundError as err:
    # The user is probably trying to run this without having installed
    # the package, so complain.
    raise RuntimeError(
        "NFTest is not correctly installed. Please install it with pip."
    ) from err
