from sanic import Sanic
from sanic import response

app = Sanic('douglass')


@app.route('/', methods=['GET'])
async def status_response(request):
    return response.text('OK')


@app.route('/api/convert')
async def convert(request):
    return response.html('<h1>HelloWorld</h1>')


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
