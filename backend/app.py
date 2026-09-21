from flask import Flask, jsonify, request
from flask_cors import CORS
from models import db, User, ServiceRequest, Proposal, Contract

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
    categories = ["Eletricidade","Canalização","Reparações","Limpeza","Tecnologia","Design"]
    return jsonify(categories)

@app.post("/api/requests")
def create_request():
    data = request.get_json(silent=True) or {}
    required = ["client_id","service","description","location"]
    missing = [x for x in required if not data.get(x)]
    if missing:
        return jsonify({"error":"Campos obrigatórios em falta","fields":missing}),400
    item = ServiceRequest(
        client_id=data["client_id"], service=data["service"],
        description=data["description"], location=data["location"],
        budget=data.get("budget"), date=data.get("date"), status="open"
    )
    db.session.add(item); db.session.commit()
    return jsonify(item.to_dict()),201

@app.get("/api/requests")
def list_requests():
    items=ServiceRequest.query.order_by(ServiceRequest.id.desc()).all()
    return jsonify([x.to_dict() for x in items])

@app.post("/api/proposals")
def create_proposal():
    data=request.get_json(silent=True) or {}
    required=["request_id","professional_id","price"]
    missing=[x for x in required if data.get(x) is None]
    if missing: return jsonify({"error":"Campos obrigatórios em falta","fields":missing}),400
    proposal=Proposal(request_id=data["request_id"],professional_id=data["professional_id"],price=data["price"],message=data.get("message",""),status="pending")
    db.session.add(proposal); db.session.commit()
    return jsonify(proposal.to_dict()),201

@app.post("/api/contracts")
def create_contract():
    data=request.get_json(silent=True) or {}
    required=["request_id","proposal_id","client_id","professional_id","price"]
    missing=[x for x in required if data.get(x) is None]
    if missing: return jsonify({"error":"Campos obrigatórios em falta","fields":missing}),400
    contract=Contract(**{k:data[k] for k in required},status="active")
    db.session.add(contract)
    req=ServiceRequest.query.get(data["request_id"])
    if req: req.status="contracted"
    db.session.commit()
    return jsonify(contract.to_dict()),201

@app.get("/api/contracts/<int:contract_id>")
def get_contract(contract_id):
    item=Contract.query.get_or_404(contract_id)
    return jsonify(item.to_dict())

if __name__ == "__main__":
    app.run(host="0.0.0.0",port=5000,debug=True)
