from app_modules.main.views import socketio, app

# You can edit the routes in the views.py file
# Start app
if __name__ == '__main__':
    socketio.run(app, port=4000, host="0.0.0.0")
