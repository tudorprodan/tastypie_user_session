
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
