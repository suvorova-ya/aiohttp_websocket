import aiohttp
import asyncio
from aiohttp import web,ClientSession

# список подключенных клиентов
clients = set()

async def handle_news(request):
    # получение новых новостей
    data = await request.json()
    async with ClientSession().ws_connect("http://127.0.0.1:6969/") as ws:
    # отправка новостей всем клиентам
     for ws in clients:
        await ws.send_str(data['news'])
        # ответ об успешной отправке новостей
        await ws.close()
    return web.Response(text="News sent to all clients")


async def websocket_handler(request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)
    clients.add(ws)
    try:
        async for msg in ws:
            if msg.type == aiohttp.WSMsgType.TEXT:
                if msg.data == 'close':
                    await ws.close()
                else:
                    await ws.send_str(msg.data)
    except aiohttp.web.WSDisconnect as e:
        print(f"websocket disconnected: {e}")
    finally:
        clients.remove(ws)
    return ws

async def check_connection():
    # проверка соединения между клиентом и сервером
    while True:
         await asyncio.sleep(30)
        # проверка соединения с клиентами
         for ws in clients:
            if ws.closed:
                clients.remove(ws)
                
                
async def index(request):
    with open('index.html') as f:
        return web.Response(text=f.read(), content_type='text/html')


async def shutdown(app):
    # закрытие соединений с клиентами при остановке сервера
    for ws in clients:
        await ws.close()

def main():
    # инициализация приложения
    app = web.Application()
    app.router.add_route('GET', '/', index)
    app.router.add_route('POST', '/news', handle_news)
    app.router.add_route('GET', '/ws', websocket_handler)
    app.on_shutdown.append(shutdown)
    web.run_app(app, host="127.0.0.1", port="6969")
   

if __name__ == '__main__':
     main()
    
    