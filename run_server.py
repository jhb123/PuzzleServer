import flaskr
from flask_socketio import SocketIO

app = flaskr.create_app()

if __name__ == '__main__':
    print("starting server")
    flaskr.socketio.run(app,host = '0.0.0.0',debug=True)
    # app.run('0.0.0.0', debug=False, port=5000)

# socketio = SocketIO(app)
#
# if __name__ == "__main__":
#      socketio.run(app)
    #

# flaskr.auth.generate_reset_password_email("foo")
