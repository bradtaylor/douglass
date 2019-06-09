from requests import get
from requests.exceptions import ConnectionError
from functools import wraps
from sanic.response import json
from nbconvert import HTMLExporter
from nbformat.v4 import to_notebook


SAM_ROOT = 'https://sam.dsde-prod.broadinstitute.org'


# Main conversion function accepting ipynb json and returning an HTML representation
# As this may be slow, it is defined as a coroutine so it can be awaited
async def perform_notebook_conversion(notebook_json):
    # Get the notebook json into a NotebookNode object that nbconvert can use
    nb = to_notebook(notebook_json)

    # set up a default nbconvert HTML exporter and run the conversion
    html_exporter = HTMLExporter()
    (nb_html, resources_dict) = html_exporter.from_notebook_node(nb)
    return nb_html


# Authorization decorator
# Decorated routes will first check the request to see if the caller is authorized to perform the operation
# If the user is unauthorized, we will respond with details rather than performing the conversion
# taken from example in Sanic documentation
# https://sanic.readthedocs.io/en/latest/sanic/decorators.html
def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # Check the Terra authorization service SAM for user auth status
            # If the user is not authorized, pass along the auth_response which details the reason
            auth_response = await check_sam_authorization(request)
            if auth_response.status != 200:
                return auth_response

            # the user is authorized.
            # run the handler method and return the response
            response = await f(request, *args, **kwargs)
            return response
        return decorated_function
    return decorator


# Query Terra's authorization service SAM to determine user authorization status. Return result as an HTTP response
async def check_sam_authorization(request):
    sam_url = SAM_ROOT + '/register/user/v2/self/info'

    # Well-formed requests must contain an authorization header
    if 'authorization' not in request.headers:
        return json({'Message': 'Bad Request. Request requires authorization header supplying Oauth2 bearer token'}, 400)
    try:
        sam_response = get(sam_url, headers={'authorization': request.headers['authorization']})
        return process_sam_response(sam_response)
    except ConnectionError:
        return json({'Message': 'Service Unavailable. Unable to contact authorization service'}, 503)


# Process the raw response from the SAM authorization service into a more useful response to return to the client
def process_sam_response(sam_response):
    # For an authorized user, we will receive a 200 status code with 'enabled: True' in the response body
    status = sam_response.status_code
    if status == 200:
        if 'enabled' not in sam_response.json():
            return json({'Message': 'Internal Server Error. Unable to determine user authorization status'}, 500)
        elif not sam_response.json()['enabled']:
            return json({'Message': 'Forbidden. User is registered in Terra, but not activated.'}, 403)
        else:
            # SAM service returned 200 and the user was enabled
            return json({'Message: Authorized'}, 200)
    # Intercept non-successful status codes and return a more helpful message
    else:
        if status == 401:
            return json({'Message': 'Unauthorized. User is not allowed in Terra or has not signed in.'}, 401)
        elif status == 403:
            return json({'Message': 'Forbidden.'}, 403)
        elif status == 404:
            return json({'Message': 'Unauthorized. User is authenticated to Google but is not a Terra member'}, 401)
        elif status == 500:
            return json({'Message': 'Internal Server Error. Authorization service query failed'}, 500)
        elif status == 503:
            return json(
                {'Message': 'Service Unavailable. Authorization service unable to contact one or more services'}, 503)
        else:
            return json({'Message': 'Internal Server Error. Unknown failure contacting authorization service.'}, 500)






