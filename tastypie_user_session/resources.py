from django.core.urlresolvers import reverse
from django.contrib.auth import login
from django.contrib.auth import logout
from django.contrib.auth import authenticate
from tastypie import fields
from tastypie.exceptions import NotFound
from tastypie.exceptions import BadRequest
from tastypie.resources import Resource
from tastypie.bundle import Bundle
from tastypie.authorization import Authorization
from tw.resources.user import UserResource


class UserSession(object):

    @classmethod
    def session_get_key(cls, request, create_if_needed=True):
        if not request.session.session_key and create_if_needed:
            request.session.create()
        return request.session.session_key

    @classmethod
    def object_for_request(cls, request):
        s = cls()
        s.id = cls.session_get_key(request)
        s.expire_date = request.session.get_expiry_date()
        s.user = None

        if request.user.is_authenticated():
            s.user = request.user

        return s


class UserSessionResource(Resource):
    id = fields.CharField(attribute="id", readonly=True)
    expire_date = fields.DateTimeField(attribute="expire_date", readonly=True)
    user = fields.ForeignKey(UserResource, attribute="user", readonly=True, null=True)

    class Meta:
        resource_name = "user_session"
        object_class = UserSession
        authorization = Authorization()

    def get_resource_uri(self, bundle_or_obj):
        obj = bundle_or_obj

        if isinstance(obj, Bundle):
            obj = obj.obj

        kwargs = {
            "resource_name": self._meta.resource_name,
            "pk": obj.id
        }

        if self._meta.api_name:
            kwargs["api_name"] = self._meta.api_name

        url = self._build_reverse_url("api_dispatch_detail", kwargs=kwargs)

        return url

    def _build_reverse_url(self, name, args=None, kwargs=None):
        ret = reverse(name, args=args, kwargs=kwargs)
        return ret


    def get_object_list(self, request):
        l = []

        try:
            obj = self._build_session_object_or_raise(request)
            l.append(obj)
        except NotFound:
            pass

        return l

    def obj_get_list(self, request=None, **kwargs):
        # TODO: implement filters?
        return self.get_object_list(request)

    def obj_get(self, request=None, **kwargs):
        return self._build_session_object_or_raise(request, kwargs["pk"])

    def obj_create(self, bundle, request=None, **kwargs):
        user = self.find_or_create_user_for_new_session(bundle, request, **kwargs)

        if not user:
            raise NotFound("No user was found with your credentials.")

        login(request, user)

        bundle.obj = self._build_session_object(request)
        bundle = self.full_hydrate(bundle)

        return bundle

    def obj_update(self, bundle, request=None, **kwargs):
        bundle.obj = self._build_session_object_or_raise(request, kwargs["pk"])
        bundle = self.full_hydrate(bundle)
        request.session.modified = True
        return bundle

    def obj_delete_list(self, request=None, **kwargs):
        raise BadRequest("This should not be used. You must specify the session id to delete.")

    def obj_delete(self, request=None, **kwargs):
        self._build_session_object_or_raise(request, pk=kwargs["pk"])
        logout(request)

    def rollback(self, bundles):
        """
            We never need to rollback.
        """
        pass

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):
        """
            You must override this.
        """
        raise NotImplementedError()

    def _build_session_object(self, request):
        return self._meta.object_class.object_for_request(request)

    def _build_session_object_or_raise(self, request, pk=None):
        key = self._meta.object_class.session_get_key(request, create_if_needed=False)

        if not key:
            raise NotFound("Session could not be found for the request.")

        if pk and pk != key:
            raise NotFound("That's not your session.")

        return self._build_session_object(request)



class FacebookAuthUserSessionResource(UserSessionResource):
    """
        This class will authenticate against
        tastypie_user_session.FacebookAuthBackend.

        You must make sure you have the auth backend enabled.

        This resource will automatically register new users.
    """

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):
        return authenticate(
            fb_use_cookie=bool(bundle.data.get("facebook_use_cookie", False)),
            fb_code=bundle.data.get("facebook_code", None),
            fb_token=bundle.data.get("facebook_token", None),
            request=request,
            register_new_users=True
        )



class DjangoAuthUserSessionResource(UserSessionResource):
    """
        This class doesn't provide registering via this
        API endpoint, it just logs in existing users.
    """

    def find_or_create_user_for_new_session(self, bundle, request, **kwargs):

        return authenticate(**bundle.data)
