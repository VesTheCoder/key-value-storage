from aiohttp import web
from handlers import routes

def start_app():
    app = web.Application()
    app.add_routes(routes)
    return app





if __name__ == "__main__":
    web.run_app(start_app(), host="localhost", port=6969)
