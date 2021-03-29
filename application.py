from os import environ
from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


application = Flask(__name__)
CORS(application)

# Get environment variables on server
USERNAME = environ.get('RDS_USERNAME')
PASSWORD = environ.get('RDS_PASSWORD')
HOSTNAME = environ.get('RDS_HOSTNAME')
PORT = environ.get('RDS_PORT')
DBNAME = environ.get('RDS_DB_NAME')
application.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}'

# To avoid warning. We do not use the Flask-SQLAlchemy event system, anyway.
application.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(application)


class XYData3(db.Model):
    id = db.Column(db.Integer, primary_key=True)  # Since "id" is builtin
    description = db.Column(db.String(256), unique=False, nullable=True)
    owner = db.Column(db.String(80), unique=False, nullable=False)
    x = db.Column(db.String(500), unique=False)
    y = db.Column(db.String(500), unique=False)

    def __repr__(self):
        return f"<Data set {self.id}>"


db.create_all()


@application.route('/info', methods=['GET'])
def show_info():
    return f"USERNAME={USERNAME}, PASSWORD={PASSWORD}, HOSTNAME={HOSTNAME}, PORT={PORT}, DBNAME={DBNAME}"


@application.route('/', methods=['GET'])
def index():
    xydatas = XYData3.query.order_by(XYData3.id).all()
    return render_template('index.html', xydatas=xydatas)


@application.route('/', methods=['POST'])
def add():
    description = request.form['description']
    owner = request.form['owner']
    x = request.form['x']
    y = request.form['y']
    new_data = XYData3(description=description, owner=owner, x=x, y=y)
    try:
        db.session.add(new_data)
        db.session.commit()
        return redirect('/')
    except Exception:
        return "There was an error adding your data set."


@application.route('/update/<int:id>', methods=['GET'])
def update_get(id):
    xydata = XYData3.query.get_or_404(id)
    return render_template('update.html', xydata=xydata)


@application.route('/update/<int:id>', methods=['POST'])
def update_post(id):
    # return "Here"
    xydata = XYData3.query.get_or_404(id)
    xydata.description = request.form['description']  # Keys are "name"s of input fields (not "id"s)
    xydata.owner = request.form['owner']
    xydata.x = request.form['x']
    xydata.y = request.form['y']
    try:
        db.session.commit()
        return redirect('/')
    except Exception:
        return "There was an error updating your task."


@application.route('/delete/<int:id>')
def delete(id):
    xydata_to_delete = XYData3.query.get_or_404(id)
    try:
        db.session.delete(xydata_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception:
        return "There was a problem deleting that data."


if __name__ == '__main__':
    application.debug = True

    # Start Flask app
    application.run()
