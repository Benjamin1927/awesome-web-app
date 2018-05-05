import logging;logging.basicConfig(level=logging.INFO)
import asyncio
from aiohttp import web


def index(request):
    return web.Response(body=b'awesome')


async def init(loop):
    app = web.Application()
    app.router.add_get('/',index)
    srv=await loop.create_server(app.make_handler(),'127.0.0.1',9000)
    logging.info('server faengt an')
    return srv

loop=asyncio.get_event_loop()
loop.run_until_complete(init(loop))
loop.run_forever()