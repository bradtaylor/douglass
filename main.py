from sanic import Sanic
from sanic import response
from utils import perform_notebook_conversion, authorized


# Webservice routing
app = Sanic('douglass')
app.config.from_pyfile('config.py')


@app.get('/')
async def status(request):
    return response.text('OK')


@app.post('/api/convert')
@authorized(app.config.SAM_ROOT)
async def convert(request):
    return response.html(await perform_notebook_conversion(request.json))


if __name__ == '__main__':
    app.run(port=8000)
