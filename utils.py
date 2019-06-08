from requests import get
from functools import wraps
from sanic.response import json
from nbconvert import HTMLExporter
from nbformat.v4 import to_notebook


SAM_ROOT = 'https://sam.dsde-prod.broadinstitute.org'


async def check_request_for_authorization_status(request):
    sam_url = SAM_ROOT + '/register/user/v2/self/info'
    sam_response = get(sam_url, headers=dict(authorization=request.headers['authorization']))
    return sam_response.status_code


# Authorization decorator; taken from example in Sanic documentation
# https://sanic.readthedocs.io/en/latest/sanic/decorators.html
def authorized():
    def decorator(f):
        @wraps(f)
        async def decorated_function(request, *args, **kwargs):
            # run some method that checks the request
            # for the client's authorization status
            auth_status = await check_request_for_authorization_status(request)

            if auth_status == 200:
                # the user is authorized.
                # run the handler method and return the response
                response = await f(request, *args, **kwargs)
                return response
            elif auth_status == 401:
                # the user is authenticated, but not authorized.
                return json({'Message': 'Unauthorized'}, 401)
            elif auth_status == 403:
                # the user is authenticated, but not authorized.
                return json({'Message': 'Forbidden'}, 403)
            else:
                return json({'Message': 'Failed to query auth service'}, 500)
        return decorated_function
    return decorator


# Define our main conversion function as a coroutine so it can be awaited
async def perform_notebook_conversion(notebook_json):
    # Get the notebook json into a NotebookNode object that nbconvert can use
    nb = to_notebook(notebook_json)

    # set up a default nbconvert HTML exporter and run the conversion
    html_exporter = HTMLExporter()
    (nb_html, resources_dict) = html_exporter.from_notebook_node(nb)
    return nb_html
