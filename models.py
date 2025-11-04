from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ImportRecord(db.Model):
    __tablename__ = 'imports'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    commodity = db.Column(db.String(200))
    year = db.Column(db.String(20))
    value = db.Column(db.Float)

class ExportRecord(db.Model):
    __tablename__ = 'exports'
    id = db.Column(db.Integer, primary_key=True)
    country = db.Column(db.String(100))
    commodity = db.Column(db.String(200))
    year = db.Column(db.String(20))
    value = db.Column(db.Float)
