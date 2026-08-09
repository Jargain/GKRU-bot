from quart import Quart
from routes import routes

app = Quart("main")
app.register_blueprint(routes)