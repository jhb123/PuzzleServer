# PuzzleServer

Start the server locally with:
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

Note, credentials must be generated for the password reset to work. Use `generate_credentials.py` to create the nessesary files. 

To generate the configuration for production, create a `config.py` containing a `SECRET_KEY` and `JWT_KEY`. Generate these strings with 
```commandline
python -c 'import secrets; print(secrets.token_hex())'
```