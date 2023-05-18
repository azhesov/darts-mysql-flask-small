import os

from flask import Flask, render_template, request, url_for, redirect, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
# Для работы системы используется фреймворк Flask, на котором основана логика работы задней части приложения,
# фреймворк SQLAlchemy используется для работы с базой данных, реализации CRUD функций необходимых для
# функционирования приложения. Библиотека CORS необходима для получения разрешений на запросы с фронтальной части
# приложения. Данная версия задней части приложения является промежуточной/экспериментальной, тк в ней реализована
# работа с базой данных, а также получение/отображение информации на Flask фронтальной части и получение/отсылка/
# /отображение информации на React фронтальную часть. В этом промежуточном этапе была реализована работа только
# с лонгридами, а также был реализован весь функционал на React для отработки всех функций и проверки кода.
# Данная задняя часть приложения может полноценно работать как с Flask фронтальной частью приложения, так и с
# react-flask-app фронтальной частью приложения

basedir = os.path.abspath(os.path.dirname(__file__))
# Конфигурация папки UPLOAD_FOLDER нужна для того чтобы определить место где будут храниться изображения
UPLOAD_FOLDER = os.path.join('staticFiles', 'images')

# Конфигурация приложения с определением места где будут храниться изображения и где будут находиться шаблоны для
# отображения фронтальной части приложения
app = Flask(__name__, template_folder='templates', static_folder='staticFiles')
# Конфигурация SQL базы данных
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'sqlite_darts.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.secret_key = 'Secret key'
CORS(app, support_credentials=True)

db = SQLAlchemy(app)


# Определение полей и связей класса LongRead (Лонгрид)
class LongRead(db.Model):
    __tablename__ = 'LongRead'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(1000), nullable=False)
    img_link = db.Column(db.String(200), nullable=True)
    text = db.Column(db.String(10000), nullable=True)

    def __repr__(self):
        return f'<LongRead {self.name}>'


if __name__ == '__main__':
    app.run()


# React Функция для создания лонгрида. При создании лонгрида ему будет присвоена стандартная фотография
@app.route('/api/longreads/create', methods=('GET', 'OPTIONS', 'POST'))
def create_longread():
    # Фронтальная часть приложения перед отправлением запроса на создание элемента отправляет OPTIONS запрос,
    # на который необходимо ответить ответом с необходимыми заголовками, в котором указаны разрешенные методы
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'POST')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return jsonify({'message': 'Approved'}), 201
    # Полученный JSON-текст парсится для извлечения из него данных
    json = request.json
    # Создание лонгрида используя данные полученные из JSON-текста
    longread = LongRead(name=json["name"], description=json["description"], text=json["text"])
    # Лонгриду присваивается стандартная фотография
    longread.img_link = "/staticFiles/images/QuestionMark.jpg"
    # Добавление нового лонгрида в сессию изменений
    db.session.add(longread)
    # Фиксация изменений в БД
    db.session.commit()
    # Отсылка сообщения
    return jsonify({'message': 'Longread created successfully'}), 201


# Функция для передачи на React фронтальную часть приложения всех лонгридов находящихся в базе данных
@app.route('/api/longreads', methods=['GET'])
def get_longreads():
    # Получение списка всех лонгридов по запросу в базу данных
    longreads = LongRead.query.all()
    data = []
    # Создание JSON-текста в котором указаны данные лонгрида
    for lr in longreads:
        item = {
            'id': lr.id,
            'name': lr.name,
            'description': lr.description,
            'img_link': 'http://127.0.0.1:5000' + lr.img_link,
            'text': lr.text
        }
        data.append(item)
    # JSON-текст перенаправляется на фронтальную часть приложения
    return jsonify(data)


# Функция для передачи на React фронтальную часть приложения информации о лонгриде по его индексу.
@app.route('/api/longreads/<int:longread_id>', methods=['GET'])
def get_longread(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Формирование JSON-текста с данными лонгрида
    data = {
        'id': longread.id,
        'name': longread.name,
        'description': longread.description,
        'img_link': 'http://127.0.0.1:5000' + longread.img_link,
        'text': longread.text
    }
    # JSON-текст перенаправляется на фронтальную часть приложения
    return jsonify(data)


# React Функция для редактирования лонгрида, идентификатор которого был указан
@app.route('/api/longreads/<int:longread_id>/edit', methods=['POST'])
def edit_longread(longread_id):
    # Полученный JSON-текст парсится для извлечения из него данных
    json = request.json
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Внесение изменений
    longread.name = json["name"]
    longread.description = json["description"]
    longread.text = json["text"]
    # Добавление измененного лонгрида в сессию изменений
    db.session.add(longread)
    # Фиксация изменений в БД
    db.session.commit()
    # Отсылка сообщения
    return jsonify({'message': 'Longread updated successfully'})


# React Функция для измененения фотографии лонгрида, идентификатор которого был указан. Предыдущее изображение
# лонгрида будет удалено, если оно не являлось стандартным
@app.route('/api/longreads/<int:longread_id>/update-image', methods=['POST'])
def update_longread_image(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Получение файла изображения из формы
    new = request.files["image"]
    # Сохранение названия файла
    filename = new.filename
    # Проверка на пустой файл
    if filename != '':
        # Проверка ссылки на изображение, для того чтобы не удалить стандартную фотографию
        if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
            # Удаление фотографии
            os.remove(longread.img_link[1:])
        # Создание уникального имени использую id лонгрида
        longread_img_name = "longread" + str(longread.id) + ".jpg"
        # Сохранение изображения в папку под уникальным именем
        new.save(os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name))
        # Внесение изменений
        longread.img_link = "/" + os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name)
    # Добавление измененного лонгрида в сессию изменений
    db.session.add(longread)
    # Фиксация изменений в БД
    db.session.commit()
    # Отсылка сообщения
    return jsonify({'message': 'Longread updated successfully'})


# React Функция для удаления лонгрида, указанного по его идентификатору, а также изображения, которое с ним связано
@app.route('/api/longreads/<int:longread_id>/delete', methods=('GET', 'OPTIONS', 'DELETE'))
def delete_longread(longread_id):
    # Фронтальная часть приложения перед отправлением запроса на удаление элемента отправляет OPTIONS запрос,
    # на который необходимо ответить ответом с необходимыми заголовками, в котором указаны разрешенные методы
    if request.method == 'OPTIONS':
        response = jsonify()
        response.headers.add('Access-Control-Allow-Origin', '*')
        response.headers.add('Access-Control-Allow-Methods', 'DELETE')
        response.headers.add('Access-Control-Allow-Headers', 'Content-Type')
        return jsonify({'message': 'Approved'}), 201
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Проверка ссылки на изображение, для того чтобы не удалить стандартную фотографию
    if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
        # Удаление фотографии
        os.remove(longread.img_link[1:])
    # Удаление лонгрида
    db.session.delete(longread)
    # Фиксация изменений в БД
    db.session.commit()
    # Отсылка сообщения
    return {'message': 'Longread deleted successfully'}


# Функция для передачи на Flask фронтальную часть приложения всех лонгридов находящихся в базе данных
@app.route('/')
def index():
    # Получение списка всех лонгридов по запросу в базу данных
    longreads = LongRead.query.all()
    # Отсылка собранных данных на фронтальную часть приложения для их отображения
    return render_template('index.html', longreads=longreads)


# Функция для передачи на Flask фронтальную часть приложения информации о лонгриде по его индексу,
# а также информации о всех связанных с ним глав
@app.route('/<int:longread_id>/')
def longread(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Отсылка собранных данных на фронтальную часть приложения для их отображения
    return render_template('longread.html', longread=longread)


# Flask Функция для создания лонгрида. При создании лонгрида ему будет присвоена стандартная фотография,
# либо фотография загруженная в форму
@app.route('/create/', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        # Получение файла изображения и данных из формы
        name = request.form['name']
        description = request.form['description']
        uploaded_img = request.files['uploaded-file']
        text = request.form['text']
        # Создание лонгрида используя данные полученные из форм
        longread = LongRead(name=name,
                          description=description,
                          text=text)
        # Добавление нового лонгрида в сессию изменений
        db.session.add(longread)
        # Использование функции flush для получения id нового лонгрида
        db.session.flush()
        # Обновление лонгрида для получения id
        db.session.refresh(longread)
        # Сохранение названия файла
        filename = uploaded_img.filename
        # Проверка на пустой файл
        if filename == '':
            # Если пустой файл лонгриду присваивается стандартная фотография
            longread.img_link = "/staticFiles/images/QuestionMark.jpg"
        else:
            # Создание уникального имени использую id лонгрида
            longread_img_name = "longread" + str(longread.id) + ".jpg"
            # Сохранение изображения в папку под уникальным именем
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name))
            # Сохранение названия файла
            longread.img_link = "/" + os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name)
        # Фиксация изменений в БД
        db.session.commit()

        return redirect(url_for('index'))

    return render_template('create.html')


# Flask Функция для редактирования лонгрида и его фотографии, используя указанный идентификатор лонгрида. Предыдущее
# изображение лонгрида будет удалено, если оно не являлось стандартным
@app.route('/<int:longread_id>/edit/', methods=('GET', 'POST'))
def edit(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    if request.method == 'POST':
        # Получение файла изображения и данных из формы
        name = request.form['name']
        description = request.form['description']
        uploaded_img = request.files['uploaded-file']
        text = request.form['text']
        # Сохранение названия файла
        filename = uploaded_img.filename
        # Проверка на пустой файл
        if filename != '':
            # Проверка ссылки на изображение, для того чтобы не удалить стандартную фотографию
            if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
                # Удаление фотографии
                os.remove(longread.img_link[1:])
            # Создание уникального имени использую id лонгрида
            longread_img_name = "longread" + str(longread.id) + ".jpg"
            # Сохранение изображения в папку под уникальным именем
            uploaded_img.save(os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name))
            # Внесение изменений
            longread.img_link = "/" + os.path.join(app.config['UPLOAD_FOLDER'], longread_img_name)
        # Внесение изменений
        longread.name = name
        longread.description = description
        longread.text = text
        # Добавление измененного лонгрида в сессию изменений
        db.session.add(longread)
        # Фиксация изменений в БД
        db.session.commit()

        return redirect(url_for('longread', longread_id=longread_id))

    return render_template('edit.html', longread=longread)


# Flask Функция для удаления фотографии лонгрида, идентификатор которого был указан. Изображение
# лонгрида будет удалено, если оно не являлось стандартным
@app.post('/<int:longread_id>/delete_longread_image/')
def delete_longread_image(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Проверка ссылки на изображение, для того чтобы не удалить стандартную фотографию
    if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
        # Удаление фотографии
        os.remove(longread.img_link[1:])
        # Лонгриду присваивается стандартная фотография
        longread.img_link = "/staticFiles/images/QuestionMark.jpg"
        # Добавление измененного лонгрида в сессию изменений
        db.session.add(longread)
        # Фиксация изменений в БД
        db.session.commit()
    return redirect(url_for('longread', longread_id=longread_id))


# Flask Функция для удаления лонгрида, указанного по его идентификатору, а также изображения, которое с ним связано
@app.post('/<int:longread_id>/delete/')
def delete(longread_id):
    # Получение лонгрида по запросу в базу данных
    longread = LongRead.query.get_or_404(longread_id)
    # Проверка ссылки на изображение, для того чтобы не удалить стандартную фотографию
    if longread.img_link != "/staticFiles/images/QuestionMark.jpg":
        # Удаление фотографии
        os.remove(longread.img_link[1:])
    # Удаление лонгрида
    db.session.delete(longread)
    # Фиксация изменений в БД
    db.session.commit()
    return redirect(url_for('index'))
