from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, ServiceRequest, Proposal, Contract, SupportTicket

app = Flask(__name__)
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kamba.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
CORS(app)
db.init_app(app)

with app.app_context():
    db.create_all()


@app.get("/api/health")
def health():
    return jsonify({"ok": True, "service": "Kamba API"})


@app.get("/api/services")
def services():
    return jsonify(["Eletricidade", "Canalização", "Reparações", "Limpeza", "Tecnologia", "Design"])


@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}
    if not data.get("name") or not data.get("phone"):
        return jsonify({"error": "Nome e telefone são obrigatórios"}), 400
    user = User(
        name=data["name"],
        phone=data["phone"],
        email=data.get("email"),
        role=data.get("role", "client"),
        location=data.get("location"),
        specialty=data.get("specialty"),
    )
    db.session.add(user)
    try:
        db.session.commit()
    except Exception:
        db.session.rollback()
        return jsonify({"error": "Telefone ou email já registado"}), 409
    return jsonify({"id": user.id, "name": user.name, "role": user.role}), 201


@app.get("/api/users/<int:user_id>")
def get_user(user_id):
    user = User.query.get_or_404(user_id)
    return jsonify({
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "role": user.role,
        "location": user.location,
        "specialty": user.specialty,
        "rating": user.rating,
    })


@app.post("/api/requests")
def create_request():
    data = request.get_json(silent=True) or {}
    required = ["client_id", "service", "description", "location"]
    missing = [x for x in required if not data.get(x)]
    if missing:
        return jsonify({"error": "Campos obrigatórios em falta", "fields": missing}), 400
    item = ServiceRequest(
        client_id=data["client_id"],
        service=data["service"],
        description=data["description"],
        location=data["location"],
        budget=data.get("budget"),
        date=data.get("date"),
        status="open",
    )
    db.session.add(item)
    db.session.commit()
    return jsonify(item.to_dict()), 201


@app.get("/api/requests")
def list_requests():
    items = ServiceRequest.query.order_by(ServiceRequest.id.desc()).all()
    return jsonify([x.to_dict() for x in items])


@app.get("/api/requests/<int:request_id>")
def get_request(request_id):
    return jsonify(ServiceRequest.query.get_or_404(request_id).to_dict())


@app.get("/api/requests/<int:request_id>/proposals")
def list_proposals(request_id):
    items = Proposal.query.filter_by(request_id=request_id).order_by(Proposal.id.desc()).all()
    return jsonify([x.to_dict() for x in items])


@app.post("/api/proposals")
def create_proposal():
    data = request.get_json(silent=True) or {}
    required = ["request_id", "professional_id", "price"]
    missing = [x for x in required if data.get(x) is None]
    if missing:
        return jsonify({"error": "Campos obrigatórios em falta", "fields": missing}), 400
    proposal = Proposal(
        request_id=data["request_id"],
        professional_id=data["professional_id"],
        price=data["price"],
        message=data.get("message", ""),
        status="pending",
    )
    db.session.add(proposal)
    db.session.commit()
    return jsonify(proposal.to_dict()), 201


@app.post("/api/contracts")
def create_contract():
    data = request.get_json(silent=True) or {}
    required = ["request_id", "proposal_id", "client_id", "professional_id", "price"]
    missing = [x for x in required if data.get(x) is None]
    if missing:
        return jsonify({"error": "Campos obrigatórios em falta", "fields": missing}), 400
    contract = Contract(**{k: data[k] for k in required}, status="active")
    db.session.add(contract)
    req = ServiceRequest.query.get(data["request_id"])
    if req:
        req.status = "contracted"
    db.session.commit()
    return jsonify(contract.to_dict()), 201


@app.get("/api/contracts/<int:contract_id>")
def get_contract(contract_id):
    return jsonify(Contract.query.get_or_404(contract_id).to_dict())


@app.post("/api/support")
def create_support_ticket():
    data = request.get_json(silent=True) or {}
    required = ["name", "contact", "topic", "message"]
    missing = [field for field in required if not str(data.get(field, "")).strip()]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing,
        }), 400

    ticket = SupportTicket(
        name=str(data["name"]).strip(),
        contact=str(data["contact"]).strip(),
        topic=str(data["topic"]).strip(),
        message=str(data["message"]).strip(),
        status="open",
    )
    db.session.add(ticket)
    db.session.commit()

    return jsonify({
        "message": "Pedido de suporte criado com sucesso.",
        "ticket": ticket.to_dict(),
    }), 201


@app.get("/api/support/<int:ticket_id>")
def get_support_ticket(ticket_id):
    return jsonify(SupportTicket.query.get_or_404(ticket_id).to_dict())


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
