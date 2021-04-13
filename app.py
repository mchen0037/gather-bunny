import os

from server import app

if __name__ == "__main__":
    app.secret_key = os.urandom(12)
    app.debug = True
    app.host = "0.0.0.0"
    app.port = 5000
    app.threaded=True
    app.run()
