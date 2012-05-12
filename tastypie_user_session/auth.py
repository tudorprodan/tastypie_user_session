import facebook
from django.contrib.auth.models import User
from django.contrib.auth.backends import ModelBackend
from django.db import models
from django.conf import settings
from tastypie.exceptions import BadRequest
from models import UserFacebookAccount

tur_settings = settings.TASTYPIE_USER_RESOURCE_SETTINGS

def wrap_graph_api_errors(fn):
    def wrapped(*args, **kwargs):
        try:
            return fn(*args, **kwargs)
        except facebook.GraphAPIError, e:
            raise BadRequest("GraphAPIError: %s" % e.message)
    return wrapped

class FacebookAuthBackend(ModelBackend):

    @wrap_graph_api_errors
    def authenticate(self, fb_use_cookie=None, fb_code=None, fb_token=None, request=None, register_new_users=False):
        access_token = None

        if fb_use_cookie:
            user = self._get_fb_user_from_cookie(request.COOKIES)
            access_token = user["access_token"]
        elif fb_code:
            code = fb_code
            access_token = self._get_access_token_from_code(code)
        elif fb_token:
            access_token = fb_token

        if not access_token:
            return None

        graph = facebook.GraphAPI(access_token)
        me = graph.get_object("me")

        user = self._get_user_for_facebook_graph(me)

        if not user and register_new_users:
            user = self._create_user_for_facebook_graph(me, graph)

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

    def _get_access_token_from_code(self, code):
        return facebook.get_access_token_from_code(
            code,
            tur_settings["facebook_code_redirect_uri"],
            tur_settings["facebook_app_id"],
            tur_settings["facebook_app_secret"]
        )

    def _get_user_for_facebook_graph(self, me):
        user = None
        fb_id = me["id"]

        if self._should_use_profile_for_facebook_id():
            profile_class = self._get_user_profile_class()
            k = "%s__exact" % tur_settings["user_profile_facebook_id_field"]
            try:
                profile = profile_class._default_manager.get(**{
                    k: fb_id
                })
                user = profile.user
            except profile_class.DoesNotExist:
                pass
        else:
            try:
                user = UserFacebookAccount.objects.get(facebook_id=fb_id).user
            except UserFacebookAccount.DoesNotExist:
                pass

        return user

    def _should_use_profile_for_facebook_id(self):
        """
            This method decides if lookup and storage of
            the user's facebook_id should be done on
            our own UserFacebookAccount model or on an
            existing field, created by the user, on UserProfile.
        """
        if "user_profile_facebook_id_field" in tur_settings:
            return True
        else:
            return False

    def _create_user_for_facebook_graph(self, me, graph):
        user = User()

        try:
            user.first_name = me["first_name"]
            user.last_name = me["last_name"]
            user.email = me["email"]
            user.username = "facebook_user_%s" % me["id"]
        except KeyError, e:
            raise BadRequest("Your facebook profile is lacking fields. Maybe you didn't ask for the proper permissions. Error was: %s", e.message)

        user.set_unusable_password()
        user.save()

        if self._should_use_profile_for_facebook_id():
            """
                Profile should be created by a post-save
                signal on User. Hopefully..
            """
            profile = user.get_profile()
            setattr(profile, tur_settings["user_profile_facebook_id_field"], me["id"])
            profile.save()
        else:
            ufa = UserFacebookAccount()
            ufa.facebook_id = me["id"]
            ufa.user = user
            ufa.save()

        return user

    def _get_user_profile_class(self):
        """
            TODO: Figure out if we should check that
            settings.AUTH_PROFILE_MODULE is properly set.
            Currently, we just assume it is and use it.
        """
        app_label, model_name = settings.AUTH_PROFILE_MODULE.split(".")
        return models.get_model(app_label, model_name)

