from flask import Flask, render_template, request, redirect, url_for, session
from utils import validateForm, parseToDate
from datetime import datetime, date
from sqlalchemy import func

app = Flask(__name__)
app.config.from_pyfile('config.py')

from models import db
from models import Trabajador, RegHorario

db.init_app(app)

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/registrar-entrada', methods = ['POST', 'GET'])
def registrarEntrada():
    if request.method == 'GET':
        return render_template('registrar_entrada.html')

    data = request.form
    try:
        validateForm(data,['legajo','dni', 'dependencia'])
        if not data['dependencia'] in ['D01','D02','D03']:
            raise ValueError('Valor de dependencia ingresado no válido')

        trabajador = db.session.query(Trabajador).filter_by(legajo=int(data['legajo'])).first()

        if not trabajador or not str(trabajador.dni).endswith(data['dni']):
            raise Exception('Trabajador no encontrado con los datos ingresados')

        foundRegistro = db.session.query(RegHorario).filter(RegHorario.fecha == datetime.now().date(), RegHorario.idtrabajador == trabajador.id).first()

        if foundRegistro:
            raise ValueError("No se puede registrar una nueva entrada ya que existe un registro activo sin un registro de salida")

        registro = RegHorario(dependencia=data['dependencia'],horaEntrada=datetime.now().time(),horaSalida=None,fecha=datetime.now().date(),idtrabajador = trabajador.id)

        db.session.add(registro)
        db.session.commit()
        
        return render_template('success.html', message="La entrada se realizó con exito!")
        
    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))


@app.route('/registrar-salida', methods = ['POST', 'GET'])
def registrarSalida():
    if request.method == 'GET':
        return render_template('registrar_salida.html')
    
    data = request.form
    try:
        validateForm(data,['legajo','dni'])

        trabajador = db.session.query(Trabajador).filter_by(legajo=int(data['legajo'])).first()

        if not trabajador or not str(trabajador.dni).endswith(data['dni']):
            return render_template('error.html')

        foundRegistro = db.session.query(RegHorario).filter(func.date(RegHorario.fecha) == datetime.now().date(), RegHorario.horaSalida == None).first()

        if not foundRegistro:
            return render_template('error.html')

        foundRegistro.horaSalida = datetime.now().time()
        db.session.commit()

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))

    return render_template('success.html', message="La salida se cargó con exito!")

@app.route('/registrar-trabajador', methods = ['POST', 'GET'])
def registrarTrabajador():
    if request.method == 'GET':
        return render_template('registrar_trabajador.html')

    data = request.form

    try:
        validateForm(data,['dni','nombre','apellido','correo','legajo','cant','funcion'])
        if data['funcion'] not in ['DO','AD','TE']:
            raise ValueError

        trabajador = Trabajador(dni=int(data['dni']),nombre=data['nombre'],apellido=data['apellido'],correo=data['correo'],legajo=int(data['legajo']),horas=int(data['cant']),funcion=data['funcion'])

        db.session.add(trabajador)
        db.session.commit()

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))

    return render_template('success.html', message="El trabajador se cargó con exito!")

@app.route('/consultar', methods = ['POST', 'GET'])
def consultar():
    if request.method == 'GET':
        return render_template('consultar.html')

    data = request.form    
    try:
        validateForm(data,['legajo','dni','fechaEntrada','fechaSalida'])

        fecha_entrada = parseToDate(data['fechaEntrada'])
        fecha_salida = parseToDate(data['fechaSalida'])

        if fecha_salida < fecha_entrada:
            raise ValueError("Fecha de salida no puede ser anterior a fecha de entrada")

        trabajador = db.session.query(Trabajador).filter_by(legajo=int(data['legajo'])).first()

        if not trabajador or not str(trabajador.dni).endswith(data['dni']):
            raise Exception("No existe un trabajador con los datos ingresados.")

        registros = db.session.query(RegHorario).filter(RegHorario.idtrabajador==trabajador.id,RegHorario.fecha.between(fecha_entrada,fecha_salida)).order_by(RegHorario.fecha).all()

        return render_template('registros.html',registros=registros)

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))

@app.route('/informar', methods = ['POST', 'GET'])
def informar():
    if request.method == 'GET':
        return render_template('informe-paso-1.html')

    data = request.form
    try:
        validateForm(data,['legajo','dni'])

        trabajador = db.session.query(Trabajador).filter_by(legajo=int(data['legajo']),funcion='AD').first()

        if not trabajador or not str(trabajador.dni).endswith(data['dni']):
            raise Exception("Trabajador no autorizado o no existente con los datos ingresados.")
        
        return render_template('informe-paso-2.html')
        
    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))

@app.route('/informe', methods = ['POST'])
def informar2():
    data = request.form
    try:
        validateForm(data,['fechaInicial','fechaFinal','funcion', 'dependencia'])

        fechaInicial = parseToDate(data['fechaInicial'])
        fechaFinal = parseToDate(data['fechaFinal'])

        query = db.session.query(RegHorario).join(Trabajador).filter(RegHorario.fecha.between(fechaInicial, fechaFinal),RegHorario.horaSalida.isnot(None))

        if data['funcion'] != 'ALL':
            query = query.filter(Trabajador.funcion == data['funcion'])

        if data['dependencia'] != 'ALL':
            query = query.filter(RegHorario.dependencia == data['dependencia'])

        registros = query.order_by(Trabajador.apellido, RegHorario.fecha).all()
        
        for reg in registros:
            entrada = datetime.combine(reg.fecha, reg.horaEntrada)
            salida = datetime.combine(reg.fecha, reg.horaSalida)
    
            horas = round((salida - entrada).total_seconds() / 3600, 2)
            reg.cant = horas

        return render_template('informe.html', registros=registros)

    except ValueError as e:
        return render_template('error.html', message=str(e))
    except Exception as e:
        return render_template('error.html', message=str(e))

if __name__ == '__main__':
    """ with app.app_context():
        db.create_all() """
    app.run(debug=True)