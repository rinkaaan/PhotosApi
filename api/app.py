import time

from apiflask import APIFlask
from flask_cors import CORS
from flask_socketio import SocketIO

from api.resources.album import album_bp
from api.resources.media import media_bp
from models.base import Base
from nguylinc_python_utils.sqlalchemy import init_sqlite_db

flask_app = APIFlask(__name__, title="Photos API", version="0.1.0", spec_path="/openapi.yaml", docs_ui="rapidoc")
socketio = SocketIO(flask_app, cors_allowed_origins="*")
session = init_sqlite_db(Base)

flask_app.config["SPEC_FORMAT"] = "yaml"
flask_app.config["LOCAL_SPEC_PATH"] = "openapi.yaml"
flask_app.config["SYNC_LOCAL_SPEC"] = True
CORS(flask_app, supports_credentials=False, origins="*", allow_headers="*")

flask_app.register_blueprint(album_bp)
flask_app.register_blueprint(media_bp)


@socketio.on("connect")
def on_connect():
    print("Client connected!")


@flask_app.teardown_appcontext
def shutdown_session(exception=None):
    if session:
        session.remove()

@flask_app.before_request
def add_fake_delay():
    # fake_delay = 100
    # fake_delay = 0.5
    fake_delay = 1
    # fake_delay = 0
    time.sleep(fake_delay)


port = 34200
BASE_URL = "http://127.0.0.1:" + str(port)

if __name__ == "__main__":
    flask_app.run(port=port, debug=True)
