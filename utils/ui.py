import os


def path(filename):
    return os.path.join(
        os.path.split(os.path.dirname(__file__))[0],
        'views',
        filename
    )
