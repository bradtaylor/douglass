from sanic import Sanic
from sanic import response
from nbconvert import HTMLExporter
from nbformat.v4 import to_notebook


# Define our main conversion function as a coroutine so it can be awaited
async def perform_conversion(notebook_json):
    # Get the notebook json into a NotebookNode object that nbconvert can use
    nb = to_notebook(notebook_json)

    # set up a default nbconvert HTML exporter and run the conversion
    html_exporter = HTMLExporter()
    (nb_html, resources_dict) = html_exporter.from_notebook_node(nb)
    return nb_html


# Webservice routing
app = Sanic('douglass')


@app.route('/', methods=['GET'])
async def status_response(request):
    return response.text('OK')


@app.route('/api/convert', methods=['POST'])
async def convert(request):
    return response.html(await perform_conversion(request.json))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
