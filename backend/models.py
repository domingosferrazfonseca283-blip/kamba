from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    phone = db.Column(db.String(40), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True)
    role = db.Column(db.String(30), default="client")
    location = db.Column(db.String(120))
    specialty = db.Column(db.String(120))
    rating = db.Column(db.Float, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)


class ServiceRequest(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    client_id = db.Column(db.Integer, nullable=False)
    service = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    location = db.Column(db.String(160), nullable=False)
    budget = db.Column(db.Float)
    date = db.Column(db.String(40))
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in ["id", "client_id", "service", "description", "location",
                      "budget", "date", "status"]
        }


class Proposal(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    professional_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    message = db.Column(db.Text)
    status = db.Column(db.String(30), default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in ["id", "request_id", "professional_id", "price",
                      "message", "status"]
        }


class Contract(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    request_id = db.Column(db.Integer, nullable=False)
    proposal_id = db.Column(db.Integer, nullable=False)
    client_id = db.Column(db.Integer, nullable=False)
    professional_id = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Float, nullable=False)
    status = db.Column(db.String(30), default="active")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            k: getattr(self, k)
            for k in ["id", "request_id", "proposal_id", "client_id",
                      "professional_id", "price", "status"]
        }


class SupportTicket(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    contact = db.Column(db.String(160), nullable=False)
    topic = db.Column(db.String(120), nullable=False)
    message = db.Column(db.Text, nullable=False)
    status = db.Column(db.String(30), default="open")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "contact": self.contact,
            "topic": self.topic,
            "message": self.message,
            "status": self.status,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
