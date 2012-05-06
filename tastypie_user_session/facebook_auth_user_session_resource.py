import facebook
from django.conf import settings
from django.db import models
from django.contrib.auth.models import User
from tastypie.exceptions import BadRequest
from user_session_resource import UserSessionResource

tur_settings = settings.TASTYPIE_USER_RESOURCE_SETTINGS

class FacebookAuthUserSessionResource(UserSessionResource):

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):
        try:
            oauth_token = None

            if "facebook_code" in bundle.data:
                code = bundle.data["facebook_code"]
                oauth_token = self._get_oauth_token_from_code(code)
            else:
                user = self._get_fb_user_from_cookie(request.COOKIES)
                oauth_token = user["access_token"]

            graph = facebook.GraphAPI(oauth_token)
            me = graph.get_object("me")

            user = self._get_user_for_facebook_graph(me)

            if not user:
                user = self._create_user_for_facebook_graph(me)

            """
                We shamelessly LIE about who authenticated the user.
                TODO: Create a custom backend, when I have time.
            """
            user.backend = "django.contrib.auth.backends.ModelBackend"

            return user

        except facebook.GraphAPIError, e:
            raise BadRequest("GraphAPIError: %s" % e.message)

    def _get_user_for_facebook_graph(self, me):
        k = "%s__exact" % tur_settings["user_profile_facebook_id_field"]
        profile_class = self._get_user_profile_class()
        user = None

        try:
            profile = profile_class._default_manager.get(**{
                k: me["id"]
            })
            user = profile.user
        except profile_class.DoesNotExist:
            pass

        return user

    def _create_user_for_facebook_graph(self, me):
        user = User()
        user.first_name = me["first_name"]
        user.last_name = me["last_name"]
        user.email = me["email"]
        user.username = me["username"]
        user.set_unusable_password()
        user.save()

        """
            Profile should be created by a post-save
            signal on User. Hopefully..
        """
        profile = user.get_profile()
        setattr(profile, tur_settings["user_profile_facebook_id_field"], me["id"])
        profile.save()

        return user

    def _get_fb_user_from_cookie(self, cookies):
        try:
            return facebook.get_user_from_cookie(
                cookies,
                tur_settings["facebook_app_id"],
                tur_settings["facebook_app_secret"]
            )
        except (ValueError, KeyError, TypeError):
            """
                We must catch these, since the facebook SDK
                raises them when provided invalid data.
                e.g. it raises TypeError if the cookie data is invalid.
            """
            raise BadRequest("Failed to parse Facebook cookie.")

    def _get_oauth_token_from_code(self, code):
        return facebook.get_access_token_from_code(
            code,
            tur_settings["facebook_code_redirect_uri"],
            tur_settings["facebook_app_id"],
            tur_settings["facebook_app_secret"]
        )

    def _get_user_profile_class(self):
        """
            TODO: Figure out if we should check that
            settings.AUTH_PROFILE_MODULE is properly set.
            Currently, we just assume it is and use it.
        """
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split(".")
        return models.get_model(app_label, model_name)


