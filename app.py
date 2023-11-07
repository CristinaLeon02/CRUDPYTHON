from flask import Flask
from flask import render_template,request,redirect,url_for,flash
from flask import send_from_directory
import pymysql
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key=("Develoteca")
def obtener_conexion():
    return pymysql.connect(host='localhost',
                                user='root',
                                password='',
                                db='sistema')

CARPETA = os.path.join('uploads')
#guardar con un valor a carpeta
app.config['CARPETA'] = CARPETA

#creamos un acceso de la imagen del permiso antes importado
@app.route('/uploads/<nombreFoto>')
def uploads(nombreFoto):
   return send_from_directory(app.config['CARPETA'], nombreFoto)

@app.route('/')
def index():
   conexion = obtener_conexion()
   with conexion.cursor() as cursor:
      sql = "SELECT * FROM  `empleados`;"
      cursor.execute(sql)
      #nos muestra en consola la consulta
      empleados = cursor.fetchall()
      print(empleados)
      
   conexion.commit()
   conexion.close()
   return render_template('empleados/index.html', empleados=empleados)

@app.route('/destroy/<int:id>')
def destroy(id):
   conexion = obtener_conexion()
   with conexion.cursor() as cursor:

      cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
      fila = cursor.fetchall()
      os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
      
      cursor.execute("DELETE FROM empleados WHERE id=%s",(id))
      conexion.commit()
      return redirect('/')
      
@app.route('/edit/<int:id>')
def edit(id):
   conexion = obtener_conexion()
   with conexion.cursor() as cursor:
      cursor.execute("SELECT * FROM  empleados WHERE id=%s",(id))
      #nos muestra en consola la consulta
      empleados = cursor.fetchall()
      print(empleados)
      conexion.commit()
   return render_template('empleados/edit.html', empleados=empleados)
     
@app.route('/create')
def create():
    return render_template('empleados/create.html')

@app.route('/update', methods = ['POST'])
def update():
   conexion = obtener_conexion()
   _nombre= request.form['txtNombre']
   _correo= request.form['txtCorreo']
   _foto= request.files['txtFoto']
   id = request.form['txtID']
   with conexion.cursor() as cursor:
      sql = "UPDATE empleados SET nombre=%s,correo=%s WHERE id=%s;"
      datos = (_nombre,_correo,id)

      now = datetime.now()
      tiempo=now.strftime("%Y%H%M%S")

      if _foto.filename!='':
         nuevoNombreFoto=tiempo+_foto.filename
         _foto.save("uploads/"+nuevoNombreFoto)

         cursor.execute("SELECT foto FROM empleados WHERE id=%s",id)
         fila = cursor.fetchall()

         os.remove(os.path.join(app.config['CARPETA'],fila[0][0]))
         cursor.execute("UPDATE empleados SET foto=%s  WHERE id=%s", (nuevoNombreFoto,id))
         conexion.commit()


      cursor.execute(sql,datos)
   conexion.commit()
   conexion.close()

   return redirect('/')

@app.route('/store', methods=['POST'])
def storage():
   conexion = obtener_conexion()
   _nombre= request.form['txtNombre']
   _correo= request.form['txtCorreo']
   _foto= request.files['txtFoto']

   if _nombre=='' or _correo=='' or _foto=='':
      flash('Recuerda llenar los datos de los campos')
      return redirect(url_for('create'))

   now = datetime.now()
   tiempo=now.strftime("%Y%H%M%S")

   if _foto.filename!='':
      nuevoNombreFoto=tiempo+_foto.filename
      _foto.save("uploads/"+nuevoNombreFoto)


   with conexion.cursor() as cursor:
      sql = "INSERT INTO `empleados` (`id`, `nombre`, `correo`, `foto`) VALUES (NULL,%s,%s,%s);"
      datos = (_nombre,_correo,nuevoNombreFoto)
      cursor.execute(sql,datos)
   conexion.commit()
   conexion.close()
   return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)