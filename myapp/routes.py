# myapp/routes.py
from flask import Blueprint, render_template, redirect, url_for, flash, request, abort
from flask_login import login_user, logout_user, current_user, login_required
from .models import User, Novel
from . import db, login_manager
from flask import jsonify

main = Blueprint('main', __name__)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# --- Otentikasi: Register, Login, Logout ---
@main.route('/api/novels')
def novels_api():
    novels = Novel.query.filter_by(approved=True).all()
    novels_data = [{
        'title': novel.title,
        'last_chapter': novel.last_chapter if novel.last_chapter else 'Belum ada update',
        'last_update': novel.last_update.strftime('%Y-%m-%d %H:%M') if novel.last_update else '-',
        'url': novel.url
    } for novel in novels]
    return jsonify(novels_data)
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.filter_by(username=username).first():
            flash("Username sudah ada!", "danger")
        else:
            new_user = User(username=username, password=password, is_admin=False)
            db.session.add(new_user)
            db.session.commit()
            flash("Registrasi berhasil, silakan login", "success")
            return redirect(url_for('main.login'))
    return render_template('register.html')

@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()  # Plain text untuk demo
        if user:
            login_user(user)
            flash("Login berhasil!", "success")
            return redirect(url_for('main.index'))
        else:
            flash("Username atau password salah", "danger")
    return render_template('login.html')

@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash("Logout berhasil!", "success")
    return redirect(url_for('main.login'))

# --- Fitur Novel ---

@main.route('/')
def index():
    novels = Novel.query.filter_by(approved=True).all()
    return render_template('index.html', novels=novels)

@main.route('/add', methods=['GET', 'POST'])
@login_required
def add_novel():
    if request.method == 'POST':
        title = request.form['title']
        url_novel = request.form['url']
        # Novel langsung di-approve jika user adalah admin
        approved = current_user.is_admin
        new_novel = Novel(title=title, url=url_novel, last_chapter="", approved=approved)
        db.session.add(new_novel)
        db.session.commit()
        if approved:
            flash("Novel berhasil ditambahkan.", "success")
        else:
            flash("Novel berhasil ditambahkan dan menunggu moderasi.", "info")
        return redirect(url_for('main.index'))
    return render_template('add_novel.html')

# --- Moderasi Novel (hanya admin) ---

@main.route('/moderate')
@login_required
def moderate():
    if not current_user.is_admin:
        abort(403)
    pending_novels = Novel.query.filter_by(approved=False).all()
    return render_template('moderate.html', novels=pending_novels)

@main.route('/approve/<int:novel_id>')
@login_required
def approve_novel(novel_id):
    if not current_user.is_admin:
        abort(403)
    novel = Novel.query.get_or_404(novel_id)
    novel.approved = True
    db.session.commit()
    flash(f"Novel '{novel.title}' telah disetujui.", "success")
    return redirect(url_for('main.moderate'))

# --- Manajemen User (hanya admin) ---

@main.route('/users')
@login_required
def user_list():
    if not current_user.is_admin:
        abort(403)
    users = User.query.all()
    return render_template('users.html', users=users)

@main.route('/promote/<int:user_id>')
@login_required
def promote(user_id):
    if not current_user.is_admin:
        abort(403)
    user = User.query.get_or_404(user_id)
    if user.is_admin:
        flash(f"{user.username} sudah merupakan admin.", "info")
    else:
        user.is_admin = True
        db.session.commit()
        flash(f"{user.username} telah dipromosikan menjadi admin.", "success")
    return redirect(url_for('main.user_list'))

# --- Route Sederhana untuk mempromosikan RegresAlfa ---
@main.route('/promote_regresalfa')
def promote_regresalfa():
    user = User.query.filter_by(username='RegresAlfa').first()
    if user:
        user.is_admin = True
        db.session.commit()
        return f"User {user.username} sudah dipromosikan menjadi admin."
    else:
        return "User 'RegresAlfa' tidak ditemukan."
