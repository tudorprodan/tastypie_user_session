__version__ = "0.2"

from resources import UserSessionResource
from resources import DjangoAuthUserSessionResource
from resources import FacebookAuthUserSessionResource

# Quiet lint warnings
if None:
    UserSessionResource
    DjangoAuthUserSessionResource
    FacebookAuthUserSessionResource
