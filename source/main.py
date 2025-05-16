from aiohttp import web

from settings import APP_HOST, APP_PORT
from handlers import routes
from scheduler import start_scheduler
from setup_db import init_database



def start_app() -> web.Application:
    """
    Initializes and configures:
    1. the aiohttp web app.
    2. database structure (if does not exists already)
    3. scheduler background daemon and expired keys cleaning on web app startup.
    """
    app = web.Application()
    app.add_routes(routes)
    app.on_startup.append(init_database)
    app.on_startup.append(start_scheduler)

    return app



if __name__ == "__main__":
    web.run_app(start_app(), host=APP_HOST, port=APP_PORT)
