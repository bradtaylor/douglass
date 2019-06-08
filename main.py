from sanic import Sanic
from sanic import response
from utils import perform_notebook_conversion, authorized


# Webservice routing
app = Sanic('douglass')


@app.get('/')
async def status(request):
    return response.text('OK')


@app.post('/api/convert')
@authorized()
async def convert(request):
    return response.html(await perform_notebook_conversion(request.json))


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
