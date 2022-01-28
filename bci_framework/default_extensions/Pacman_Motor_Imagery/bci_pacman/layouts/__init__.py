import os


# ----------------------------------------------------------------------
def get_layouts():
    """"""
    files = os.listdir(os.path.dirname(__file__))
    return list(filter(lambda s: s.endswith('.lay'), files))
