from app_modules.main.views import socketio, app

# You can edit the routes in the views.py file
# Start app
socketio.run(app, debug=True, port=5000)
