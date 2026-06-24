"""
models.py

Defines the Patient table.

Using Flask-SQLAlchemy here so I don't have to write raw SQL for the
CRUD operations - it maps this class straight to a SQLite table.
"""

from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class Patient(db.Model):
    __tablename__ = "patients"

    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(120), nullable=False)
    date_of_birth = db.Column(db.Date, nullable=False)
    email = db.Column(db.String(120), nullable=False)

    glucose = db.Column(db.Float, nullable=False)
    haemoglobin = db.Column(db.Float, nullable=False)
    cholesterol = db.Column(db.Float, nullable=False)

    # this gets filled in automatically by the ML model, not by the user
    remarks = db.Column(db.Text, nullable=True)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        # just makes debugging in the python shell easier, not used by the app
        return f"<Patient {self.id} - {self.full_name}>"