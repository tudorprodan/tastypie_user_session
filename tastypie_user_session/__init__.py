__version__ = "0.1"

from user_session import UserSession
from user_session_resource import UserSessionResource
from django_auth_user_session_resource import DjangoAuthUserSessionResource
from facebook_auth_user_session_resource import FacebookAuthUserSessionResource

# Quiet lint warnings
if None:
    UserSession
    UserSessionResource
    DjangoAuthUserSessionResource
    FacebookAuthUserSessionResource
