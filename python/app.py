import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

app = Flask(__name__)


app.config.from_object(os.environ['APP_SETTINGS'])
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

from models import State, County

@app.route('/')
def index():
    result = db.session.query(State).all()
    print(result)
    return str(result)

@app.route('/state/<state>')
def county_cases(state):
    result = db.session.query(County).join(State).filter(func.lower(State.name) == func.lower(state)).all()
    print(result)
    return str(result)


if __name__ == '__main__':
    app.run()