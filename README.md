## This packages provides:

```python
# yourapp/api.py

from tastypie_user_session import FacebookAuthUserSessionResource

v1_api = Api(api_name="v1")
v1_api.register(FacebookAuthUserSessionResource())
```

## You can:

```
- GET /api/v1/user_session/
  - see if you have an active session
- PUT /api/v1/user_session/<session_key>/
  - refresh your session
- POST /api/v1/user_session/
  - create a new session (login) with a new or existing user for the app
    - via the Facebook JS SDK cookie (empty request body)
    - via your own facebook auth code ({"facebook_code": "<your_users_facebook_code>"})
- DELETE /api/v1/user_session/<session_key>/
  - delete the session (logout)
```


## Also included:

### DjangoAuthUserSessionResource

Allows users to authenticate with any backend by POSTing credentials.  
User creation is not supported, because I have not implemented it, but could be added.

### UserSessionResource

This is the base class, which is meant to be extended by _you_ to achieve the behavior you want.

Both `FacebookAuthUserSessionResource` and `DjangoAuthUserSessionResource` override a single method from this class:  
```python
def find_or_create_user_for_new_session(self, bundle, request, **kwargs)
```


### Warning

This is work in progress.

`UserSessionResource` is written to be extended by others.

`FacebookAuthUserSessionResource` is written to suit my specific needs, but I hope it either works for yours as well, or inspires you on how to customize the base class.





