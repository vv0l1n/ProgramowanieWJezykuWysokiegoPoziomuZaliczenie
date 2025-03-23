from App import app


@app.route('/')
def hello_world():
    return 'Hello World'