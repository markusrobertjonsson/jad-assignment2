from os import environ
# import threading
# import sys
# import json
# from json import JSONEncoder
from flask import Flask, render_template, request, redirect, url_for  # , jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# from dotenv import load_dotenv


application = Flask(__name__)
CORS(application)

# basedir = path.abspath(path.dirname(__file__))
# load_dotenv(path.join(basedir, '.env'))

# mysql+mysqlconnector://<user>:<password>@<host>[:<port>]/<dbname>
# app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hejsan123@localhost/testdatabasen'

# Get environment variables on server
USERNAME = environ.get('RDS_USERNAME')
PASSWORD = environ.get('RDS_PASSWORD')
HOSTNAME = environ.get('RDS_HOSTNAME')
PORT = environ.get('RDS_PORT')
DBNAME = environ.get('RDS_DB_NAME')
application.config['SQLALCHEMY_DATABASE_URI'] = f'mysql+pymysql://{USERNAME}:{PASSWORD}@{HOSTNAME}:{PORT}/{DBNAME}'

# application.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+mysqlconnector://root:hejsan123@localhost:3306/minlokala'


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

    # def get(self, attribute_name):
    #     d = self.serialize()
    #     return d[attribute_name]

    # def update(self, new_data):
    #     for key, value in new_data.items():
    #         setattr(self, key, value)

    # def serialize(self):
    #     return {'id': self.id,
    #             'x': self.x,
    #             'y': self.y,
    #             'description': self.description,
    #             'owner': self.owner}

    # def to_string(self):
    #     d = self.serialize()
    #     out_str = f"{d['id']}: "
    #     for key, val in d.items():
    #         if key != 'id':
    #             out_str += f"{key}: {val}    "
    #     return out_str


db.create_all()

# xydata = XYData3(description="A descr", owner="MJ", x="1,2,3", y="3,2,1")
# db.session.add(xydata)
# db.session.commit()


@application.route('/foo', methods=['GET'])
def foo():
    return "Hello World!"


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


# @application.route('/xydata', methods=['POST'])
# def create_xydata():
#     dc = json.loads(request.data)

#     # XXX
#     # print(dc)
#     # dc.pop('id', None)
#     # dc['id'] = 1

#     xydata = XYData3(**dc)
#     add_xydata_to_db(xydata)
#     url = url_for('get_xydata', id=xydata.id)
#     return redirect(url)


# def add_xydata_to_db(xydata):
#     db.session.add(xydata)
#     db.session.commit()


# @application.route('/xydata', methods=['GET'])
# def get_all_xydata():
#     all_xydata = XYData3.query.all()
#     all_xydata_serialized = [xydata.serialize() for xydata in all_xydata]
#     return jsonify(all_xydata_serialized)


# def get_all_xydata_str():
#     all_xydata = XYData3.query.all()
#     out_str = ""
#     for xydata in all_xydata:
#         out_str += xydata.to_string() + "\n"
#     return out_str


# @application.route('/<int:id>', methods=['GET'])
# def get_xydata(id):
#     xydata = XYData3.query.filter_by(id=id).one()
#     return jsonify(xydata.serialize())


# def get_xydata_obj(id):
#     xydata = XYData3.query.filter_by(id=id).one()
#     return xydata


# @application.route('/xydata/<int:id>', methods=['PUT'])
# def update_old(id):
#     xydata = XYData3.query.filter_by(id=id).one()
#     dc = json.loads(request.data)
#     xydata.update(dc)
#     db.session.commit()
#     return jsonify(xydata.serialize())


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
    # xydata.id = request.form['id']
    try:
        db.session.commit()
        return redirect('/')
    except Exception:
        return "There was an error updating your task."


# @application.route('/xydata/<int:id>', methods=['DELETE'])
# def delete_xydata(id):
#     xydata = XYData3.query.filter_by(id=id).one()
#     db.session.delete(xydata)
#     db.session.commit()
#     return ""


@application.route('/delete/<int:id>')
def delete(id):
    xydata_to_delete = XYData3.query.get_or_404(id)
    try:
        db.session.delete(xydata_to_delete)
        db.session.commit()
        return redirect('/')
    except Exception:
        return "There was a problem deleting that data."

# cli_thread = threading.Thread(target=command_line)
# cli_thread.start()  # Start command line loop


if __name__ == '__main__':
    application.debug = True

    # Start Flask app
    application.run()












# from flask import Flask

# # print a nice greeting.
# def say_hello(username="World"):
#     return '<p>Hello %s!</p>\n' % username


# # some bits of text for the page.
# header_text = '''
#     <html>\n<head> <title>EB Flask Test</title> </head>\n<body>'''
# instructions = '''
#     <p><em>Hint</em>: This is a RESTful web service! Append a username
#     to the URL (for example: <code>/Thelonious</code>) to say hello to
#     someone specific.</p>\n'''
# home_link = '<p><a href="/">Back</a></p>\n'
# footer_text = '</body>\n</html>'

# # EB looks for an 'application' callable by default.
# application = Flask(__name__)

# # add a rule for the index page.
# # application.add_url_rule('/', 'index', (lambda: header_text + say_hello() + instructions + footer_text))

# # add a rule when the page is accessed with a name appended to the site
# # URL.
# # application.add_url_rule('/<username>', 'hello', (lambda username: header_text + say_hello(username) + home_link + footer_text))


# @application.route('/foo', methods=['GET'])
# def foo():
#     return "My foo Hello World!"


# # run the app.
# if __name__ == "__main__":
#     # Setting debug to True enables debug output. This line should be
#     # removed before deploying a production app.
#     application.debug = True
#     application.run()
