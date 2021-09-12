from app.main.views import socketio, app

if __name__ == '__main__':
    # You can edit the routes in the views.py file
    # Start app
    # app.run(debug=True, host='0.0.0.0', port=5000)
    socketio.run(app, debug=True, port=5000)
