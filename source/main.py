from aiohttp import web

from settings import APP_HOST, APP_PORT
from handlers import routes
from scheduler import start_scheduler

def start_app() -> web.Application:
    """
    Initializes and configures the aiohttp web app.
    Initializes scheduler background task on web app startup.
    """
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(start_scheduler)

    return app



if __name__ == "__main__":
    web.run_app(start_app(), host=APP_HOST, port=APP_PORT)
