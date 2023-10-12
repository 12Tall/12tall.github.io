import uvicorn
import fastapi


async def app(scope, receive, send):
    assert scope['type'] == 'http'

    await send({
        'type': 'http.response.start',
        'status': 200,
        'headers': [[b'content-type', b'text/plain']]
    })

    await send({
        'type':'http.response.body',
        'body':b'Hello, World!'
    })


if __name__ == '__main__':
    uvicorn.run('main:app', port=5000, log_level='info')