from flask_mysqldb import MySQL
from flask import Flask, render_template, request, redirect, url_for, session, flash
from werkzeug.security import generate_password_hash, check_password_hash
import stripe
import smtplib
from email.mime.text import MIMEText
import random
from config import Config

app = Flask(__name__)
app.secret_key = 'miclave123'
app.config.from_object(Config)

mysql = MySQL(app)

usuarios = {}
codigos_verificacion = {}

productos = {
    "1": {
        "nombre": "Polo Negro",
        "precio": 49.90,
        "descripcion": "Polo de algodón negro",
        "imagen": "polonegro.jpg"
    },
    "2": {
        "nombre": "Streetwear Jackets",
        "precio": 129.90,
        "descripcion": "Chaqueta urbana",
        "imagen": "casaca.jpg"
    },
    "3": {
        "nombre": "Pantalon blanco",
        "precio": 99.90,
        "descripcion": "Pantalón blanco",
        "imagen": "pants.jpg"
    },
    "4": {
        "nombre": "SPECIAL 4:20 2.0",
        "precio": 149.90,
        "descripcion": "Edición especial",
        "imagen": "west.jpg"
    },
    "5": {
        "nombre": "Air Force 1",
        "precio": 499.90,
        "descripcion": "Zapatillas clásicas",
        "imagen": "zapas1.jpg"
    }
}

def enviar_codigo_por_correo(destinatario, codigo):
    remitente = 'averr.leca12@gmail.com'
    clave_app = 'ouet fxai oiha qkdw'
    mensaje = MIMEText(f'Tu código de recuperación es: {codigo}')
    mensaje['Subject'] = 'Código de recuperación de contraseña'
    mensaje['From'] = remitente
    mensaje['To'] = destinatario

    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as smtp:
        smtp.login(remitente, clave_app)
        smtp.send_message(mensaje)

@app.route('/')
def inicio():
    return render_template('inicio.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        usuario = request.form['username']
        if usuario in usuarios:
            flash("Usuario ya registrado")
            return redirect(url_for('register'))

        usuarios[usuario] = {
            "email": request.form['email'],
            "password": generate_password_hash(request.form['password'])
        }

        flash("Registrado correctamente. Ahora inicia sesión.")
        return redirect(url_for('login'))

    return render_template('register.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        usuario = request.form['username']
        clave = request.form['password']
        user = usuarios.get(usuario)
        if user and check_password_hash(user['password'], clave):
            session['usuario'] = usuario
            return redirect(url_for('catalogo'))
        flash("Usuario o clave incorrecta")
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('usuario', None)
    session.pop('carrito', None)
    return redirect(url_for('login'))

@app.route('/catalogo')
def catalogo():
    
        

    carrito = session.get('carrito', {})
    total = 0.0

    if carrito:
        for item in carrito.values():
            try:
                total += float(item['precio']) * int(item['cantidad'])
            except:
                continue

    return render_template('catalogo.html', productos=productos, total=total if carrito else None)

@app.route('/agregar/<pid>')
def agregar(pid):
    if 'carrito' not in session:
        session['carrito'] = {}

    carrito = session['carrito']
    global productos  # o usar directamente si está global

    if pid in productos:
        producto = productos[pid]
        if pid in carrito:
            carrito[pid]['cantidad'] += 1
        else:
            carrito[pid] = {
                'nombre': producto['nombre'],
                'precio': producto['precio'],
                'cantidad': 1
            }
        session['carrito'] = carrito
        flash('Producto agregado al carrito', 'success')
    else:
        flash('Producto no válido', 'danger')

    return redirect(url_for('catalogo'))



@app.route('/carrito')
def ver_carrito():
    carrito = session.get('carrito', {})
    total = sum(float(item['precio']) * int(item['cantidad']) for item in carrito.values())
    return render_template('carrito.html', carrito=carrito, total=total)

@app.route('/aumentar/<int:pid>')
def aumentar(pid):
    if 'carrito' not in session:
        return redirect(url_for('ver_carrito'))

    carrito = session['carrito']
    str_pid = str(pid)

    if str_pid in carrito:
        carrito[str_pid]['cantidad'] += 1
        session['carrito'] = carrito

    return redirect(url_for('ver_carrito'))

@app.route('/quitar/<int:pid>')
def quitar(pid):
    if 'carrito' not in session:
        return redirect(url_for('ver_carrito'))

    str_pid = str(pid)
    carrito = session['carrito']

    if str_pid in carrito:
        if carrito[str_pid]['cantidad'] > 1:
            carrito[str_pid]['cantidad'] -= 1
        else:
            del carrito[str_pid]  # Elimina el producto si llega a 0
        session['carrito'] = carrito

    return redirect(url_for('ver_carrito'))

@app.route('/eliminar/<int:pid>')
def eliminar(pid):
    if 'carrito' in session:
        carrito = session['carrito']
        str_pid = str(pid)
        if str_pid in carrito:
            del carrito[str_pid]
            session['carrito'] = carrito
    return redirect(url_for('ver_carrito'))


@app.route('/pagar', methods=['POST'])
def pagar():
    carrito = session.get('carrito', {})
    if not carrito:
        return redirect(url_for('ver_carrito'))

    line_items = [
    {
        'price_data': {
            'currency': 'pen',
            'unit_amount': int(float(item['precio']) * 100),
            'product_data': {'name': item['nombre']}
        },
        'quantity': item['cantidad']
    } for item in carrito.values()
]

    session['carrito'] = {}
    checkout = stripe.checkout.Session.create(
        payment_method_types=['card'],
        line_items=line_items,
        mode='payment',
        success_url=url_for('exito_pago', _external=True),
        cancel_url=url_for('ver_carrito', _external=True)
    )
    return redirect(checkout.url)





@app.route('/pago_manual')
def pago_manual():
    return render_template('pago_manual.html')

@app.route('/exito')
def exito_pago():
    return render_template('pago_exito.html')

@app.route('/olvide-contrasena', methods=['GET', 'POST'])
def olvide_contrasena():
    if request.method == 'POST':
        correo = request.form['email']
        usuario = next((u for u in usuarios if usuarios[u]['email'] == correo), None)
        if usuario:
            codigo = str(random.randint(100000, 999999))
            codigos_verificacion[correo] = codigo
            enviar_codigo_por_correo(correo, codigo)
            session['correo_recuperacion'] = correo
            flash('Se ha enviado un código a tu correo.')
            return redirect(url_for('verificar_codigo'))
        else:
            flash('Correo no encontrado.')
    return render_template('olvide_contrasena.html')

@app.route('/verificar-codigo', methods=['GET', 'POST'])
def verificar_codigo():
    correo = session.get('correo_recuperacion')
    if not correo:
        return redirect(url_for('login'))

    if request.method == 'POST':
        codigo = request.form['codigo']
        if codigos_verificacion.get(correo) == codigo:
            flash('Código correcto. Cambia tu contraseña.')
            return redirect(url_for('cambiar_contrasena'))
        else:
            flash('Código incorrecto.')
    return render_template('verificar_codigo.html')

@app.route('/cambiar-contrasena', methods=['GET', 'POST'])
def cambiar_contrasena():
    correo = session.get('correo_recuperacion')
    if not correo:
        return redirect(url_for('login'))

    if request.method == 'POST':
        nueva = request.form['nueva_contrasena']
        repetir = request.form['repetir_contrasena']
        if nueva != repetir:
            flash('Las contraseñas no coinciden.')
            return redirect(url_for('cambiar_contrasena'))

        for usuario, datos in usuarios.items():
            if datos['email'] == correo:
                datos['password'] = generate_password_hash(nueva)
                flash('Contraseña cambiada con éxito. Inicia sesión.')
                session.pop('correo_recuperacion', None)
                return redirect(url_for('login'))
        flash('Correo no registrado.')
    return render_template('cambiar_contrasena.html')

if __name__ == '__main__':
    app.run(debug=True)