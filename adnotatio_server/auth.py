from collections import namedtuple


AdnotatioAuthorInfo = namedtuple("AdnotatioAuthorInfo", ['name', 'email', 'avatar'])


def default_author_resolver():
    return AdnotatioAuthorInfo(None, None, None)
