import os

from flask import Flask, render_template, request, url_for, redirect
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

basedir = os.path.abspath(os.path.dirname(__file__))
UPLOAD_FOLDER = os.path.join('staticFiles', 'images')

app = Flask(__name__, template_folder='templates', static_folder='staticFiles')
app.config['SQLALCHEMY_DATABASE_URI'] = \
    'sqlite:///' + os.path.join(basedir, 'sqlite_darts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Secret key'

db = SQLAlchemy(app)


class LongRead(db.Model):
    __tablename__ = 'LongRead'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    img_link = db.Column(db.String(200), nullable=True)
    text = db.Column(db.String(10000), nullable=True)

    def __repr__(self):
        return f'<LongRead {self.name}>'


@app.route('/')
def index():
    longreads = LongRead.query.all()
    return render_template('index.html', longreads=longreads)


@app.route('/<int:longread_id>/')
def longread(longread_id):
    longread = LongRead.query.get_or_404(longread_id)
    return render_template('longread.html', longread=longread)


@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        uploaded_img = request.files['uploaded-file']
        text = request.form['text']
        longread = LongRead(name=name,
                          description=description,
                          text=text)
        db.session.add(longread)
        db.session.flush()
        db.session.refresh(longread)
        filename = uploaded_img.filename
        if filename == '':
            longread.img_link = "/staticFiles/images/QuestionMark.jpg"
        else:
            longread_img_name = "longread" + str(longread.id) + ".jpg"
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name))
            longread.img_link = "/" + os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name)
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


@app.route('/<int:longread_id>/edit/', methods=('GET', 'POST'))
def edit(longread_id):
    longread = LongRead.query.get_or_404(longread_id)

    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        uploaded_img = request.files['uploaded-file']
        text = request.form['text']
        filename = uploaded_img.filename
        if filename != '':
            if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
                os.remove(longread.img_link[1:])
            longread_img_name = "longread" + str(longread.id) + ".jpg"
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name))
            longread.img_link = "/" + os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name)
        longread.name = name
        longread.description = description
        longread.text = text

        db.session.add(longread)
        db.session.commit()

        return redirect(url_for('longread', longread_id=longread_id))

    return render_template('edit.html', longread=longread)


@app.post('/<int:longread_id>/delete_longread_image/')
def delete_longread_image(longread_id):
    longread = LongRead.query.get_or_404(longread_id)
    if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
        os.remove(longread.img_link[1:])
        longread.img_link = "/staticFiles/images/QuestionMark.jpg"
        db.session.add(longread)
        db.session.commit()
    return redirect(url_for('longread', longread_id=longread_id))


@app.post('/<int:longread_id>/delete/')
def delete(longread_id):
    longread = LongRead.query.get_or_404(longread_id)
    if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
        os.remove(longread.img_link[1:])
    db.session.delete(longread)
    db.session.commit()
    return redirect(url_for('index'))
