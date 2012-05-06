This packages provides:

```python
# yourapp/api.py

from tastypie_user_session import FacebookAuthUserSessionResource

v1_api = Api(api_name="v1")
v1_api.register(FacebookAuthUserSessionResource())
```

You can now:

- `GET /api/v1/user_session/`
  - see if you have an active session
- `PUT /api/v1/user_session/<session_key>/`
  - refresh your session
- `POST /api/v1/user_session/`
  - create a new session (login) with a new or existing user for the app
    - via the Facebook JS SDK cookie
    - via your own facebook auth code
- `DELETE /api/v1/user_session/<session_key>/`
  - delete the session (logout)
