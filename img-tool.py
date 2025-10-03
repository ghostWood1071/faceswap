from idlelib.window import add_windows_to_menu

from ui import cmd_app
import sys
import asyncio
import copy
from uvicorn import Server, Config

async def cmd_app_init(args):
    argv = args[1:]
    return await cmd_app.main(argv)

async def web_app_init(args):
   config = Config("ui.webapp.api:app", port=8001, reload=True)
   server = Server(config)
   await server.serve()

async def web_app_run(args):
    pass

entry_point = {
    "cmd": cmd_app_init,
    "web": web_app_init
}

async def main(args):
    print(args)
    app_mode = args[1]
    app_type = await entry_point.get(app_mode)(args)


if __name__ == "__main__":
    asyncio.run(main(sys.argv))