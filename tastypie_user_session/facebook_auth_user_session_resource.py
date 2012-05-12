from django.contrib.auth import authenticate
from user_session_resource import UserSessionResource

class FacebookAuthUserSessionResource(UserSessionResource):

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):
        """
            This class will authenticate against
            tastypie_user_session.FacebookAuthBackend.

            You must make sure you have the auth backend enabled.

            This resource will automatically register new users.
        """
        return authenticate(
            fb_use_cookie=bool(bundle.data.get("facebook_use_cookie", False)),
            fb_code=bundle.data.get("facebook_code", None),
            fb_token=bundle.data.get("facebook_token", None),
            request=request,
            register_new_users=True
        )
