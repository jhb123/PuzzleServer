import flaskr

app = flaskr.create_app()

if __name__ == '__main__':
    print("starting server")
    flaskr.socketio.run(app,host = '0.0.0.0',debug=True)
