This package lets you authenticate via `tastypie` using cookies.

This is the ideal way to authenticate for example in a `Backbone.js` client application.

`__version__ = "0.2"`

## Installation

```bash
# grab the code from github
pip install -e git://github.com/tudorprodan/tastypie_user_session.git#egg=tastypie-user-session
# or PyPI
pip install tastypie-user-session
```

`yourapp/api.py` :
```python
from tastypie_user_session import FacebookAuthUserSessionResource

v1_api = Api(api_name="v1")
v1_api.register(FacebookAuthUserSessionResource())
```

`settings.py` :
```python
INSTALLED_APPS += ("tastypie_user_session", )

TASTYPIE_USER_RESOURCE_SETTINGS = {
    "facebook_app_id": "<your_app_id>",
    "facebook_app_secret": "<your_app_secret>"
}
```

## Usage

- `GET /api/v1/user_session/` - see if you have an active session
- `PUT /api/v1/user_session/<session_key>/` - refresh your session, empty request body
- `DELETE /api/v1/user_session/<session_key>/`- delete the session (logout)
- `POST /api/v1/user_session/` - create a new session (login) with a new or existing user for the app
    - using the Facebook JS SDK cookie, request body: `{ "facebook_use_cookie": true }`
    - via a Facebook oauth code, request body: `{ "facebook_code": "<users_fb_oauth_code>" }`
    - via a Facebook auth token, request body: `{ "facebook_token": "<users_fb_token>" }`

As long as the client keeps using the same cookiejar (the way browsers do), he is now authenticated by `django.contrib.auth`'s middleware automatically.


## Also provided

### DjangoAuthUserSessionResource

Allows users to authenticate with any backend by POSTing credentials.  
User creation is not supported, because I have not implemented it, but could be added.

### UserSessionResource

This is the base class, which is meant to be extended by _you_ to achieve the behavior you want.

Both `FacebookAuthUserSessionResource` and `DjangoAuthUserSessionResource` override a single method from this class:  
```python
def find_or_create_user_for_new_session(self, bundle, request, **kwargs)
```


## Customization

### Using an existing Facebook ID field on `UserProfile`

Suppose you already have a Facebook ID associated with your users, e.g. you used it for something else:

```python
class UserProfile(models.Model):
    ...
    fb_id = models.CharField(max_length=255)
    ...
```

`tastypie_user_session.FacebookAuthUserSessionResource` can use it:

```python
# settings.py
TASTYPIE_USER_RESOURCE_SETTINGS["user_profile_facebook_id_field"] = "fb_id"
```

Now, instead of using it's own `FacebookAuthUser` model, it will use `UserProfile.fb_id` to store and look up user's Facebook ID.


### Using Facebook's Oauth dialog

As described [here](https://developers.facebook.com/docs/authentication/), you can use Facebook's Oauth dialog to get a user authorization code, which can then be exchanged for an access token. In order to do the exchange, we need the redirect URI used by the client (FB API requirement).

```python
# settings.py
TASTYPIE_USER_RESOURCE_SETTINGS["facebook_code_redirect_uri"] = "http://www.mysite.com/facebook_oauth_landing_page.html"
```


### Notes

I'm already using `FacebookAuthUserSessionResource` successfully on two projects.

You can very easily extend `UserSessionResource` to suit your needs and authenticate in any way you want. (e.g. LDAP)






