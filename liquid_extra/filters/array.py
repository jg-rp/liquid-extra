from liquid.filter import array_filter


@array_filter
def index(arr, obj):
    """Return the first zero-based index of an item in an array. Or None if
    the items is not in the array.
    """
    try:
        return arr.index(obj)
    except ValueError:
        return None
