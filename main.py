from blog import app
from blog.views import socketio

if __name__ == '__main__':
    socketio.run(app, debug=True)