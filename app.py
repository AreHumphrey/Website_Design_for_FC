from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from werkzeug.utils import secure_filename
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # Max 16MB upload size

db = SQLAlchemy(app)

# Database models
class Content(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    text = db.Column(db.Text, nullable=False)

class GalleryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(150), nullable=False)
    filetype = db.Column(db.String(10), nullable=False)  # "image" or "video"

class FooterContent(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    image = db.Column(db.String(150), nullable=True)
    text = db.Column(db.Text, nullable=True)

# Routes
@app.route('/')
def home():
    content = Content.query.first()
    gallery_items = GalleryItem.query.all()
    footer_content = FooterContent.query.first()
    return render_template('index.html', content=content, gallery_items=gallery_items, footer_content=footer_content)

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
        elif action == 'update_footer':
            footer_text = request.form.get('footer_text')
            footer_image = request.files.get('footer_image')
            footer = FooterContent.query.first()
            if not footer:
                footer = FooterContent()
                db.session.add(footer)

            if footer_text:
                footer.text = footer_text

            if footer_image:
                filename = secure_filename(footer_image.filename)
                filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                footer_image.save(filepath)
                footer.image = filename

            db.session.commit()

        return redirect(url_for('admin'))

    content = Content.query.first()
    gallery_items = GalleryItem.query.all()
    footer_content = FooterContent.query.first()
    return render_template('admin.html', content=content, gallery_items=gallery_items, footer_content=footer_content)

# Static section content
@app.context_processor
def inject_static_content():
    static_section = {
        "logo": "static/images/logo.svg",
        "title": "Танцевально-спортивный <br> коллектив",
        "menu": [
            {"id": "about", "name": "Описание"},
            {"id": "leader", "name": "Руководитель"},
            {"id": "gallery", "name": "Галерея"},
            {"id": "contact", "name": "Контакты"}
        ],
        "sections": [
            {"id": "about", "title": "Описание", "content": "Текст описания коллектива...", "image": "static/images/description_image.jpg"},
            {"id": "leader", "title": "Руководитель", "content": "Наталья Геннадьевна Солодкая - Руководитель коллектива 'Ласточка' и Мастер спорта...", "image": "static/images/leader_image.jpg"}
        ]
    }
    return dict(static_section=static_section)

# Initialize database
with app.app_context():
    db.create_all()
    if not Content.query.first():
        db.session.add(Content(text="Здесь будет описание сайта."))
        db.session.commit()
    if not FooterContent.query.first():
        db.session.add(FooterContent(text="Подвал сайта."))
        db.session.commit()

if __name__ == '__main__':
    app.run(debug=True)