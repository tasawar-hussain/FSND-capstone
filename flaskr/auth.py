import json
from functools import wraps
from urllib.request import urlopen

from flask import request
from jose import jwt

AUTH0_DOMAIN = 'poma.auth0.com'
ALGORITHMS = ['RS256']
API_AUDIENCE = 'trivia'


# NOTE: Most of the code taken from https://github.com/udacity/FSND/blob/master/BasicFlaskAuth/app.py

# AuthError Exception
'''
AuthError Exception
A standardized way to communicate auth failure modes
'''


class AuthError(Exception):
    '''A standardized way to communicate auth failure modes'''

    def __init__(self, error, status_code):
        """
        Constructor for AuthError

        :param self:
        :param error:
        :param status_code:
        """
        self.error = error
        self.status_code = status_code


# Auth Header

def get_token_auth_header():
    """
    it should attempt to get the header from the request
        it should raise an AuthError if no header is present
    it should attempt to split bearer and the token
        it should raise an AuthError if the header is malformed
    return the token part of the header
    """
    # Obtains the Access Token from the Authorization Header
    authorization = request.headers.get('Authorization', None)

    if not authorization:
        raise AuthError({
            'success': False,
            'message': 'Unauthorized',
            'error': 401
        }, 401)

    token_type, token_value, extra = authorization.split(' ')
    if token_type.lower() != 'bearer':
        raise AuthError({
            'success': False,
            'message': 'Missing bearer',
            'error': 401
        }, 401)

    if not token_value:
        raise AuthError({
            'success': False,
            'message': 'Missing token',
            'error': 401
        }, 401)

    if extra:
        raise AuthError({
            'success': False,
            'message': 'Invalid format',
            'error': 401
        }, 401)

    return token_value


def check_permissions(permission, payload):
    """
    @INPUTS
        permission: string permission (i.e. 'post:drink')
        payload: decoded jwt payload

    it should raise an AuthError if permissions are not included in the payload
        !!NOTE check your RBAC settings in Auth0
    it should raise an AuthError if the requested permission string is not in the payload permissions array
    return true otherwise
    """

    if 'permissions' in payload and permission in payload['permissions']:
        return True

    raise AuthError({
        'success': False,
        'error': 403,
        'message': 'Unauthorized'
    }, 403)


def verify_decode_jwt(token):
    """
     @INPUTS
        token: a json web token (string)

    it should be an Auth0 token with key id (kid)
    it should verify the token using Auth0 /.well-known/jwks.json
    it should decode the payload from the token
    it should validate the claims
    return the decoded payload

    !!NOTE urlopen has a common certificate error described here: https://stackoverflow.com/questions/50236117/scraping-ssl-certificate-verify-failed-error-for-http-en-wikipedia-org
    """
    jsonurl = urlopen(f'https://{AUTH0_DOMAIN}/.well-known/jwks.json')
    jwks = json.loads(jsonurl.read())
    unverified_header = jwt.get_unverified_header(token)
    rsa_key = {}
    if 'kid' not in unverified_header:
        raise AuthError({
            'code': 'invalid_header',
            'description': 'Authorization malformed.'
        }, 401)

    for key in jwks['keys']:
        if key['kid'] == unverified_header['kid']:
            rsa_key = {
                'kty': key['kty'],
                'kid': key['kid'],
                'use': key['use'],
                'n': key['n'],
                'e': key['e']
            }
    if rsa_key:
        try:
            payload = jwt.decode(
                token,
                rsa_key,
                algorithms=ALGORITHMS,
                audience=API_AUDIENCE,
                issuer='https://' + AUTH0_DOMAIN + '/'
            )

            return payload

        except jwt.ExpiredSignatureError:
            raise AuthError({
                'code': 'token_expired',
                'description': 'Token expired.'
            }, 401)

        except jwt.JWTClaimsError:
            raise AuthError({
                'code': 'invalid_claims',
                'description': 'Incorrect claims. Please, check the audience and issuer.'
            }, 401)
        except Exception:
            raise AuthError({
                'code': 'invalid_header',
                'description': 'Unable to parse authentication token.'
            }, 400)
    raise AuthError({
        'code': 'invalid_header',
                'description': 'Unable to find the appropriate key.'
    }, 400)


def requires_auth(permission=''):
    def requires_auth_decorator(f):
        @wraps(f)
        def wrapper(*args, **kwargs):
            token = get_token_auth_header()
            payload = verify_decode_jwt(token)
            check_permissions(permission, payload)
            return f(payload, *args, **kwargs)
        return wrapper
    return requires_auth_decorator
