from app import init_app

server = init_app(config_file="config.json")

# A little experiment with middleware
#
# def process_project_path(request: Request):
#     print('Running process_project_path')
#     print(request.url.path)
#     print(request.path_params)


# @server.middleware("http")
# async def process(request: Request, call_next):
#     if "projects" in request.url.path:
#         process_project_path(request)
#     response = await call_next(request)
#     return response
