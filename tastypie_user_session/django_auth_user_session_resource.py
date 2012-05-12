from django.contrib.auth import authenticate
from user_session_resource import UserSessionResource


class DjangoAuthUserSessionResource(UserSessionResource):

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):
        """
            This class doesn't provide registering
            via this API endpoint, it just logs in
            existing users.
        """

        return authenticate(
            username=bundle.data["username"],
            password=bundle.data["password"]
        )
