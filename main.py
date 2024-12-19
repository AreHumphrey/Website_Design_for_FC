import os

def create_project_structure(project_name):
    # Основные папки
    directories = [
        project_name,
        f"{project_name}/templates",
        f"{project_name}/static",
        f"{project_name}/static/uploads",
        f"{project_name}/static/css",
        f"{project_name}/static/js",
    ]

    # Создание папок
    for directory in directories:
        os.makedirs(directory, exist_ok=True)
        print(f"Created directory: {directory}")

    # Основные файлы
    files = {
        f"{project_name}/app.py": get_app_py_content(),
        f"{project_name}/templates/index.html": get_index_html_content(),
        f"{project_name}/templates/admin.html": get_admin_html_content(),
        f"{project_name}/static/css/styles.css": get_css_content(),
    }

    # Создание файлов
    for file_path, content in files.items():
        with open(file_path, "w", encoding="utf-8") as f:
            f.write(content)
        print(f"Created file: {file_path}")

def get_app_py_content():
    return '''from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB upload size

db = SQLAlchemy(app)

class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    filetype = db.Column(db.String(10), nullable=False)

@app.route('/')
def home():
    content = Content.query.first()
    gallery_items = GalleryItem.query.all()
    return render_template('index.html', content=content, gallery_items=gallery_items)

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'POST':
        action = request.form.get('action')
        if action == 'update_text':
            text = request.form.get('content_text')
            content = Content.query.first()
            if not content:
                content = Content(text=text)
                db.session.add(content)
            else:
                content.text = text
            db.session.commit()
        elif action == 'upload_file':
            file = request.files['file']
            if file:
                filename = secure_filename(file.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                file.save(filepath)
                filetype = 'image' if file.mimetype.startswith('image') else 'video'
                gallery_item = GalleryItem(filename=filename, filetype=filetype)
                db.session.add(gallery_item)
                db.session.commit()
        elif action == 'delete_file':
            file_id = request.form.get('file_id')
            gallery_item = GalleryItem.query.get(file_id)
            if gallery_item:
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], gallery_item.filename)
                if os.path.exists(filepath):
                    os.remove(filepath)
                db.session.delete(gallery_item)
                db.session.commit()
        return redirect(url_for('admin'))
    content = Content.query.first()
    gallery_items = GalleryItem.query.all()
    return render_template('admin.html', content=content, gallery_items=gallery_items)

@app.before_first_request
def create_tables():
    db.create_all()
    if not Content.query.first():
        db.session.add(Content(text="Здесь будет описание сайта."))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)
'''

def get_index_html_content():
    return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Главная страница</title>
</head>
<body>
    <h1>{{ content.text }}</h1>
    <div class="gallery">
        {% for item in gallery_items %}
            {% if item.filetype == 'image' %}
                <img src="{{ url_for('static', filename='uploads/' + item.filename) }}" alt="Image">
            {% else %}
                <video controls>
                    <source src="{{ url_for('static', filename='uploads/' + item.filename) }}">
                </video>
            {% endif %}
        {% endfor %}
    </div>
</body>
</html>
'''

def get_admin_html_content():
    return '''<!DOCTYPE html>
<html lang="ru">
<head>
    <meta charset="UTF-8">
    <title>Админка</title>
</head>
<body>
    <h1>Админка</h1>
    <form method="POST" action="/admin" enctype="multipart/form-data">
        <textarea name="content_text">{{ content.text }}</textarea>
        <button type="submit" name="action" value="update_text">Сохранить</button>
    </form>
    <form method="POST" action="/admin" enctype="multipart/form-data">
        <input type="file" name="file">
        <button type="submit" name="action" value="upload_file">Загрузить</button>
    </form>
</body>
</html>
'''

def get_css_content():
    return '''body { font-family: Arial, sans-serif; }
h1 { text-align: center; }
.gallery { display: flex; flex-wrap: wrap; gap: 10px; }
img, video { max-width: 200px; }
'''

# Запуск функции
create_project_structure("flask_project")
