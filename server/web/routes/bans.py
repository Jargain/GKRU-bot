from routes import routes

@routes.route('/')
async def index():
    return "Api v0.1a"