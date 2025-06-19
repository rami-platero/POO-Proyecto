from __main__ import app
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class Trabajador(db.Model):
    __tablename__= 'trabajador'
    id = db.Column(db.Integer, primary_key=True)
    dni = db.Column(db.Integer, nullable=False)
    nombre = db.Column(db.String(20), nullable=False)
    apellido = db.Column(db.String(20), nullable=False)
    correo = db.Column(db.String(40), nullable=False, unique= True)
    legajo = db.Column(db.Integer, nullable = False, unique=True)
    horas = db.Column(db.Integer, nullable = False)   
    funcion = db.Column(db.String(2), nullable = False) 
    regHorarios = db.relationship('RegHorario', backref='trabajador', cascade="all, delete-orphan")
	
class RegHorario(db.Model):
    __tablename__= "registrohorario"
    id = db.Column(db.Integer, primary_key=True)
    dependencia = db.Column(db.String(3), nullable = False)
    fecha = db.Column(db.Date, nullable = False)
    horaEntrada = db.Column(db.Time, nullable = False)
    horaSalida = db.Column(db.Time)
    idtrabajador = db.Column(db.Integer, db.ForeignKey('trabajador.id'))