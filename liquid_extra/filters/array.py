from liquid.filter import Filter


class Index(Filter):
    """Return the first zero-based index of an item in an array. Or None if
    the items is not in the array.
    """

    name = "index"

    def __call__(self, arr, obj):
        try:
            return arr.index(obj)
        except ValueError:
            return None
