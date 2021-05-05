import warnings

from liquid.filter import Filter
from liquid.filter import array_filter


class Index(Filter):
    """Return the first zero-based index of an item in an array. Or None if
    the items is not in the array.
    """

    name = "index"

    def __init__(self, env):
        super().__init__(env)
        warnings.warn(
            "the class-based `Index` filter is depreciated and will be removed in a "
            "future release. Please use ``liquid_extra.filters.index`` instead.",
            DeprecationWarning,
            stacklevel=2,
        )

    def __call__(self, arr, obj):
        try:
            return arr.index(obj)
        except ValueError:
            return None


@array_filter
def index(arr, obj):
    """Return the first zero-based index of an item in an array. Or None if
    the items is not in the array.
    """
    try:
        return arr.index(obj)
    except ValueError:
        return None
