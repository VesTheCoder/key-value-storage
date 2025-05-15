from aiohttp import web
from handlers import routes
from scheduler import start_scheduler

def start_app():
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(start_scheduler)

    return app



if __name__ == "__main__":
    web.run_app(start_app(), host="localhost", port=6969)
