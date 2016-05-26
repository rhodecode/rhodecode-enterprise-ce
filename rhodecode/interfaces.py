
from zope.interface import Attribute, Interface


class IUserRegistered(Interface):
    """
    An event type that is emitted whenever a new user registers a user
    account.
    """
    user = Attribute('The user object.')
    session = Attribute('The session while processing the register form post.')
