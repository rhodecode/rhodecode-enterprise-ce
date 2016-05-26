
from zope.interface import implementer
from rhodecode.interfaces import IUserRegistered


@implementer(IUserRegistered)
class UserRegistered(object):
    """
    An instance of this class is emitted as an :term:`event` whenever a user
    account is registered.
    """
    def __init__(self, user, session):
        self.user = user
        self.session = session
