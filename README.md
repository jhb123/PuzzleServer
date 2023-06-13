# PuzzleServer

This server uses redis and flask to implement the server from the crossword app. The current way to start the server is
```commandline
python run_server.py
```

## Redis
Start the redis sever with
```commandline
brew services start redis
```
Stop the redis server with
```commandline
brew services stop redis
```
## Flask
To use gevent and websockets, start the server with
```commandline
gunicorn -k gevent -w 1 run_server:app
```

Start the server with:
```commandline
gunicorn -w 4 -b 0.0.0.0:5000 run_server:app
```

Start server in debug mode with
```commandline
flask --app flaskr run --debug
```
Start server to run on local network
```commandline
flask --app flaskr run --debug --host 0.0.0.0
```

Initialise database with
```commandline
flask --app flaskr init-db
```

Stop the server with `ctrl+C`

Note, credentials must be generated for the password reset to work.