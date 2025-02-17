from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
import re

app = Flask(__name__)
app.secret_key = 'supersecretkey'


# Función para verificar las credenciales
def check_credentials(username, password):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE username = ? AND password = ?', (username, password))
    user = cursor.fetchone()
    conn.close()
    return user


# Función para validar la contraseña
def validate_password(password):
    if len(password) < 8:
        return "La contraseña debe tener al menos 8 caracteres."
    if not re.search(r'[A-Z]', password):  # Al menos una mayúscula
        return "La contraseña debe tener al menos una letra mayúscula."
    if not re.search(r'[0-9]', password):  # Al menos un número
        return "La contraseña debe tener al menos un número."
    return None  # Contraseña válida


# Función para registrar un nuevo usuario
def register_user(username, password):
    # Validar la contraseña
    password_error = validate_password(password)
    if password_error:
        return password_error  # Devolver el error si la contraseña no es válida

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()

    # Verificar si el nombre de usuario ya existe
    cursor.execute('SELECT * FROM users WHERE username = ?', (username,))
    existing_user = cursor.fetchone()
    if existing_user:
        conn.close()
        return "El nombre de usuario ya existe."  # El usuario ya existe

    # Insertar nuevo usuario
    cursor.execute('''
    INSERT INTO users (username, password, role) 
    VALUES (?, ?, 'user')
    ''', (username, password))

    conn.commit()
    conn.close()
    return "Usuario registrado exitosamente."  # Si todo es correcto


@app.route('/')
def home():
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']
    user = check_credentials(username, password)

    if user:
        session['user_id'] = user[0]
        session['role'] = user[3]
        if user[3] == 'admin':
            return redirect(url_for('admin_dashboard'))
        else:
            return redirect(url_for('user_dashboard'))
    else:
        flash('Credenciales incorrectas', 'error')
        return redirect(url_for('home'))


@app.route('/register')
def register():
    return render_template('register.html')


@app.route('/register_user', methods=['POST'])
def register_user_route():
    username = request.form['username']
    password = request.form['password']
    confirm_password = request.form['confirm_password']

    # Verificar que las contraseñas coinciden
    if password != confirm_password:
        flash('Las contraseñas no coinciden.', 'error')
        return redirect(url_for('register'))

    result = register_user(username, password)  # Llamar a la función para registrar
    if "exitosamente" in result:  # Si el registro fue exitoso
        flash(result, 'success')
        return redirect(url_for('home'))
    else:  # Si hubo algún error (como usuario duplicado o contraseña inválida)
        flash(result, 'error')
        return redirect(url_for('register'))


@app.route('/user_dashboard')
def user_dashboard():
    if 'role' not in session or session['role'] != 'user':
        return redirect(url_for('home'))
    return render_template('dashboard.html', role='User')


@app.route('/admin_dashboard')
def admin_dashboard():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    return render_template('dashboard.html', role='Admin')


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('role', None)
    return redirect(url_for('home'))


# Función para eliminar lógicamente a un usuario
def delete_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_deleted = 1 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# Función para restaurar un usuario eliminado
def restore_user(user_id):
    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('UPDATE users SET is_deleted = 0 WHERE id = ?', (user_id,))
    conn.commit()
    conn.close()


# Ruta para ver la lista de usuarios
@app.route('/admin/users')
def users_list():
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))

    conn = sqlite3.connect('users.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE is_deleted = 0')
    users = cursor.fetchall()
    conn.close()

    return render_template('users_list.html', users=users)


# Ruta para eliminar un usuario
@app.route('/admin/delete_user/<int:user_id>')
def delete_user_route(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    delete_user(user_id)
    return redirect(url_for('users_list'))


# Ruta para restaurar un usuario
@app.route('/admin/restore_user/<int:user_id>')
def restore_user_route(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return redirect(url_for('home'))
    restore_user(user_id)
    return redirect(url_for('users_list'))
#almost done
if __name__ == '__main__':
    app.run(debug=True)
