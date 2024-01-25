import time

from apiflask import APIFlask
from flask_cors import CORS
from flask_socketio import SocketIO

from api.resources.album import album_bp
from api.resources.media import media_bp
from models.base import Base
from nguylinc_python_utils.sqlalchemy import init_sqlite_db

app = APIFlask(__name__, title="Photos API", version="0.1.0", spec_path="/openapi.yaml", docs_ui="rapidoc")
socketio = SocketIO(app, cors_allowed_origins="*")
session = init_sqlite_db(Base)

app.config["SPEC_FORMAT"] = "yaml"
app.config["LOCAL_SPEC_PATH"] = "openapi.yaml"
app.config["SYNC_LOCAL_SPEC"] = True
CORS(app, supports_credentials=False, origins="*", allow_headers="*")

app.register_blueprint(album_bp)
app.register_blueprint(media_bp)


@socketio.on("connect")
def on_connect():
    print("Client connected!")


@app.teardown_appcontext
def shutdown_session(exception=None):
    if session:
        session.remove()


@app.before_request
def add_fake_delay():
    # fake_delay = 100
    # fake_delay = 0.5
    # fake_delay = 1
    fake_delay = 0
    time.sleep(fake_delay)


port = 34200
BASE_URL = "http://127.0.0.1:" + str(port)

if __name__ == "__main__":
    app.run(port=port, debug=True)
