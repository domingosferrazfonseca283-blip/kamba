from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_migrate import Migrate
from models import (
    db,
    User,
    ServiceRequest,
    Proposal,
    Contract,
    Review,
    CompanyAccess,
    CompanySession,
    AuthSession,
    SupportTicket
)
from sqlalchemy import func
import os
import secrets
import hashlib
import hmac
from datetime import datetime, timedelta

app = Flask(__name__)

database_url = os.environ.get("DATABASE_URL")

if database_url:
    # Alguns provedores ainda fornecem postgres://
    if database_url.startswith("postgres://"):
        database_url = database_url.replace(
            "postgres://",
            "postgresql://",
            1
        )

    app.config["SQLALCHEMY_DATABASE_URI"] = database_url
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///kamba.db"

app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

CORS(app)
db.init_app(app)
migrate = Migrate(app, db)

MASTER_KEY = os.environ.get("KAMBA_MASTER_KEY")

if not MASTER_KEY:
    raise RuntimeError(
        "KAMBA_MASTER_KEY não configurada. "
        "Defina esta variável de ambiente antes de iniciar o backend."
    )


def user_dict(user):
    return {
        "id": user.id,
        "name": user.name,
        "phone": user.phone,
        "email": user.email,
        "role": user.role,
        "location": user.location,
        "specialty": user.specialty,
        "rating": user.rating or 0
    }


def hash_token(token):
    return hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()


def create_auth_session(user):
    token = secrets.token_urlsafe(32)

    session = AuthSession(
        user_id=user.id,
        token_hash=hash_token(token),
        active=True,
        expires_at=datetime.utcnow() + timedelta(days=30)
    )

    db.session.add(session)
    db.session.commit()

    return token, session


def get_auth_session():
    authorization = request.headers.get(
        "Authorization",
        ""
    ).strip()

    if not authorization:
        return None

    parts = authorization.split(None, 1)

    if len(parts) != 2:
        return None

    scheme, token = parts

    if scheme.lower() != "bearer" or not token.strip():
        return None

    session = AuthSession.query.filter_by(
        token_hash=hash_token(token.strip()),
        active=True
    ).first()

    if not session:
        return None

    now = datetime.utcnow()

    if session.revoked_at is not None:
        session.active = False
        db.session.commit()
        return None

    if session.expires_at <= now:
        session.active = False
        db.session.commit()
        return None

    return session


@app.get("/api/health")
def health():
    return jsonify({
        "ok": True,
        "service": "Kamba API"
    })


@app.post("/api/users")
def create_user():
    data = request.get_json(silent=True) or {}

    required = ["name", "phone"]
    missing = [x for x in required if not data.get(x)]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    phone = str(data["phone"]).strip()
    email = str(data.get("email", "")).strip() or None

    existing = User.query.filter_by(phone=phone).first()

    if existing:
        return jsonify({
            "error": "Já existe uma conta com este número."
        }), 409

    if email:
        existing_email = User.query.filter_by(email=email).first()

        if existing_email:
            return jsonify({
                "error": "Já existe uma conta com este email."
            }), 409

    role = data.get("role", "client")

    # Utilizadores normais não podem criar contas administrativas
    if role in ["admin", "team"]:
        role = "client"

    user = User(
        name=str(data["name"]).strip(),
        phone=phone,
        email=email,
        role=role,
        location=data.get("location"),
        specialty=data.get("specialty")
    )

    db.session.add(user)
    db.session.commit()

    return jsonify(user_dict(user)), 201


@app.post("/api/login")
def login():
    data = request.get_json(silent=True) or {}

    phone = str(
        data.get("phone", "")
    ).strip()

    if not phone:
        return jsonify({
            "error": "Número de telefone obrigatório."
        }), 400

    user = User.query.filter_by(
        phone=phone
    ).first()

    if not user:
        return jsonify({
            "error": "Conta não encontrada."
        }), 404

    if user.role in ["admin", "team"]:
        return jsonify({
            "error": "Esta conta pertence à área empresarial."
        }), 403

    token, session = create_auth_session(user)

    return jsonify({
        "token": token,
        "token_type": "Bearer",
        "expires_at": session.expires_at.isoformat(),
        "user": user_dict(user)
    }), 200


@app.get("/api/me")
def me():
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    return jsonify({
        "user": user_dict(session.user),
        "session": {
            "id": session.id,
            "expires_at": session.expires_at.isoformat()
        }
    }), 200


@app.post("/api/logout")
def logout():
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    session.active = False
    session.revoked_at = datetime.utcnow()

    db.session.commit()

    return jsonify({
        "ok": True,
        "message": "Sessão encerrada."
    }), 200


def get_company_session():
    token = request.headers.get("X-Company-Token", "").strip()

    if not token:
        return None

    token_hash = hashlib.sha256(
        token.encode("utf-8")
    ).hexdigest()

    session = CompanySession.query.filter_by(
        token_hash=token_hash,
        active=True
    ).first()

    if not session:
        return None

    if session.expires_at < datetime.utcnow():
        session.active = False
        db.session.commit()
        return None

    return session


@app.post("/api/admin/company-login")
def company_login():
    data = request.get_json(silent=True) or {}

    email = str(data.get("email", "")).strip().lower()
    key = str(data.get("key", "")).strip()

    if not email or not key:
        return jsonify({"error": "Email e chave são obrigatórios."}), 400

    user = User.query.filter(
        func.lower(User.email) == email
    ).first()

    if not user or user.role not in ["admin", "team"]:
        return jsonify({"error": "Acesso não autorizado à área empresarial."}), 403

    access = CompanyAccess.query.filter_by(
        user_id=user.id,
        active=True
    ).first()

    if not access:
        return jsonify({"error": "Esta conta não possui acesso empresarial ativo."}), 403

    submitted_hash = hashlib.sha256(
        key.encode("utf-8")
    ).hexdigest()

    if not hmac.compare_digest(submitted_hash, access.key_hash):
        return jsonify({"error": "Email ou chave inválidos."}), 403

    raw_token = secrets.token_urlsafe(48)

    token_hash = hashlib.sha256(
        raw_token.encode("utf-8")
    ).hexdigest()

    session = CompanySession(
        user_id=user.id,
        token_hash=token_hash,
        active=True,
        expires_at=datetime.utcnow() + timedelta(hours=12)
    )

    db.session.add(session)
    db.session.commit()

    result = user_dict(user)
    result["area"] = access.area
    result["token"] = raw_token
    result["is_admin"] = user.role == "admin"

    return jsonify(result), 200


@app.post("/api/admin/team-login")
def team_login():
    data = request.get_json(silent=True) or {}
    phone = str(data.get("phone", "")).strip()

    if not phone:
        return jsonify({
            "error": "Telefone obrigatório."
        }), 400

    user = User.query.filter_by(phone=phone).first()

    if not user or user.role not in ["admin", "team"]:
        return jsonify({
            "error": "Acesso não autorizado à área empresarial."
        }), 403

    return jsonify(user_dict(user)), 200


@app.post("/api/admin/team")
def create_team_member():
    master_key = request.headers.get("X-Master-Key", "")

    if master_key != MASTER_KEY:
        return jsonify({
            "error": "Chave mestra inválida."
        }), 403

    data = request.get_json(silent=True) or {}

    name = str(data.get("name", "")).strip()
    phone = str(data.get("phone", "")).strip()
    email = str(data.get("email", "")).strip() or None

    if not name or not phone:
        return jsonify({
            "error": "Nome e telefone são obrigatórios."
        }), 400

    if User.query.filter_by(phone=phone).first():
        return jsonify({
            "error": "Já existe uma conta com este telefone."
        }), 409

    if email and User.query.filter_by(email=email).first():
        return jsonify({
            "error": "Já existe uma conta com este email."
        }), 409

    member = User(
        name=name,
        phone=phone,
        email=email,
        role="team",
        location=data.get("location")
    )

    db.session.add(member)
    db.session.commit()

    return jsonify(user_dict(member)), 201


@app.get("/api/services")
def services():
    categories = [
        "Eletricidade",
        "Canalização",
        "Reparações",
        "Limpeza",
        "Tecnologia",
        "Design"
    ]
    return jsonify(categories)


@app.post("/api/requests")
def create_request():
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    user = session.user

    if not user or user.role != "client":
        return jsonify({
            "error": "Apenas clientes podem criar pedidos."
        }), 403

    data = request.get_json(silent=True) or {}

    required = [
        "service",
        "description",
        "location"
    ]

    missing = [x for x in required if not data.get(x)]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    item = ServiceRequest(
        client_id=user.id,
        service=str(data["service"]).strip(),
        description=str(data["description"]).strip(),
        location=str(data["location"]).strip(),
        budget=data.get("budget"),
        date=data.get("date"),
        status="open"
    )

    db.session.add(item)
    db.session.commit()

    return jsonify(item.to_dict()), 201


@app.get("/api/requests")
def list_requests():
    session = get_company_session()

    if not session:
        return jsonify({
            "error": "Sessão empresarial inválida ou expirada."
        }), 403

    user = User.query.get(session.user_id)

    if not user or user.role not in ["admin", "team"]:
        return jsonify({
            "error": "Acesso não autorizado."
        }), 403

    items = ServiceRequest.query.order_by(
        ServiceRequest.id.desc()
    ).all()

    return jsonify([x.to_dict() for x in items])


@app.get("/api/requests/client/<int:client_id>")
def list_client_requests(client_id):
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    user = session.user

    if not user or user.role != "client":
        return jsonify({
            "error": "Apenas clientes podem consultar os próprios pedidos."
        }), 403

    if client_id != user.id:
        return jsonify({
            "error": "Não autorizado a consultar pedidos deste cliente."
        }), 403

    items = ServiceRequest.query.filter_by(
        client_id=user.id
    ).order_by(ServiceRequest.id.desc()).all()

    return jsonify([x.to_dict() for x in items])


@app.get("/api/requests/<int:request_id>/proposals")
def list_request_proposals(request_id):
    request_item = ServiceRequest.query.get_or_404(request_id)

    items = Proposal.query.filter_by(
        request_id=request_item.id
    ).order_by(Proposal.id.desc()).all()

    return jsonify([x.to_dict() for x in items])


@app.post("/api/proposals/<int:proposal_id>/accept")
def accept_proposal(proposal_id):
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    user = session.user

    if not user or user.role != "client":
        return jsonify({
            "error": "Apenas clientes podem aceitar propostas."
        }), 403

    proposal = Proposal.query.get_or_404(proposal_id)
    request_item = ServiceRequest.query.get_or_404(
        proposal.request_id
    )

    if request_item.client_id != user.id:
        return jsonify({
            "error": "Não tens permissão para aceitar propostas deste pedido."
        }), 403

    if proposal.status != "pending":
        return jsonify({
            "error": "Esta proposta já não está disponível."
        }), 409

    if request_item.status != "open":
        return jsonify({
            "error": "Este pedido já não está disponível."
        }), 409

    Proposal.query.filter_by(
        request_id=proposal.request_id
    ).update({"status": "rejected"})

    proposal.status = "accepted"

    contract = Contract.query.filter_by(
        request_id=request_item.id
    ).first()

    if not contract:
        contract = Contract(
            request_id=request_item.id,
            proposal_id=proposal.id,
            client_id=request_item.client_id,
            professional_id=proposal.professional_id,
            price=proposal.price,
            status="active"
        )

        db.session.add(contract)

    request_item.status = "contracted"

    db.session.commit()

    return jsonify({
        "message": "Proposta aceite e contrato criado com sucesso.",
        "proposal": proposal.to_dict(),
        "request": request_item.to_dict(),
        "contract": contract.to_dict()
    }), 200


@app.post("/api/proposals")
def create_proposal():
    session = get_auth_session()

    if not session:
        return jsonify({
            "error": "Não autenticado."
        }), 401

    user = session.user

    if not user or user.role != "professional":
        return jsonify({
            "error": "Apenas profissionais podem enviar propostas."
        }), 403

    data = request.get_json(silent=True) or {}

    required = [
        "request_id",
        "price"
    ]

    missing = [
        x for x in required
        if data.get(x) is None
    ]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    try:
        request_id = int(data["request_id"])
        price = float(data["price"])
    except (TypeError, ValueError):
        return jsonify({
            "error": "request_id e price devem possuir valores válidos."
        }), 400

    if request_id <= 0:
        return jsonify({
            "error": "request_id inválido."
        }), 400

    if price < 0:
        return jsonify({
            "error": "O preço não pode ser negativo."
        }), 400

    request_item = ServiceRequest.query.get(request_id)

    if not request_item:
        return jsonify({
            "error": "Pedido não encontrado."
        }), 404

    if request_item.status != "open":
        return jsonify({
            "error": "Este pedido não está disponível para novas propostas."
        }), 409

    existing = Proposal.query.filter_by(
        request_id=request_item.id,
        professional_id=user.id
    ).first()

    if existing:
        return jsonify({
            "error": "Já enviaste uma proposta para este pedido."
        }), 409

    proposal = Proposal(
        request_id=request_item.id,
        professional_id=user.id,
        price=price,
        message=str(data.get("message", "")).strip(),
        status="pending"
    )

    try:
        db.session.add(proposal)
        db.session.commit()
    except Exception:
        db.session.rollback()
        raise

    return jsonify(proposal.to_dict()), 201


@app.post("/api/contracts")
def create_contract():
    data = request.get_json(silent=True) or {}

    required = [
        "request_id",
        "proposal_id",
        "client_id",
        "professional_id",
        "price"
    ]

    missing = [
        x for x in required
        if data.get(x) is None
    ]

    if missing:
        return jsonify({
            "error": "Campos obrigatórios em falta",
            "fields": missing
        }), 400

    contract = Contract(
        request_id=data["request_id"],
        proposal_id=data["proposal_id"],
        client_id=data["client_id"],
        professional_id=data["professional_id"],
        price=data["price"],
        status="active"
    )

    db.session.add(contract)

    req = ServiceRequest.query.get(data["request_id"])

    if req:
        req.status = "contracted"

    db.session.commit()

    return jsonify(contract.to_dict()), 201


@app.get("/api/contracts/<int:contract_id>")
def get_contract(contract_id):
    item = Contract.query.get_or_404(contract_id)
    return jsonify(item.to_dict())


@app.patch("/api/contracts/<int:contract_id>/status")
def update_contract_status(contract_id):
    contract = Contract.query.get_or_404(contract_id)

    data = request.get_json(silent=True) or {}
    status = str(data.get("status", "")).strip()

    allowed = [
        "active",
        "in_progress",
        "completed",
        "cancelled",
        "disputed"
    ]

    if status not in allowed:
        return jsonify({
            "error": "Estado de contrato inválido."
        }), 400

    if contract.status == "completed":
        return jsonify({
            "error": "Este contrato já foi concluído."
        }), 409

    contract.status = status

    request_item = ServiceRequest.query.get(
        contract.request_id
    )

    if request_item:
        if status == "completed":
            request_item.status = "completed"
        elif status == "cancelled":
            request_item.status = "cancelled"

    db.session.commit()

    return jsonify({
        "message": "Estado do contrato atualizado.",
        "contract": contract.to_dict()
    }), 200


@app.get("/api/contracts/professional/<int:professional_id>")
def list_professional_contracts(professional_id):
    items = Contract.query.filter_by(
        professional_id=professional_id
    ).order_by(Contract.id.desc()).all()

    return jsonify([x.to_dict() for x in items])


@app.get("/api/contracts/client/<int:client_id>")
def list_client_contracts(client_id):
    items = Contract.query.filter_by(
        client_id=client_id
    ).order_by(Contract.id.desc()).all()

    return jsonify([x.to_dict() for x in items])


@app.post("/api/contracts/<int:contract_id>/review")
def create_review(contract_id):
    data = request.get_json(silent=True) or {}

    contract = Contract.query.get_or_404(contract_id)

    client_id = data.get("client_id")

    if client_id is None:
        return jsonify({
            "error": "Cliente obrigatório."
        }), 400

    if int(client_id) != contract.client_id:
        return jsonify({
            "error": "Este cliente não pode avaliar este contrato."
        }), 403

    if contract.status != "completed":
        return jsonify({
            "error": "Só podes avaliar depois de o contrato ser concluído."
        }), 409

    existing = Review.query.filter_by(
        contract_id=contract.id
    ).first()

    if existing:
        return jsonify({
            "error": "Este contrato já foi avaliado."
        }), 409

    try:
        rating = int(data.get("rating"))
    except (TypeError, ValueError):
        return jsonify({
            "error": "A avaliação deve ser de 1 a 5."
        }), 400

    if rating < 1 or rating > 5:
        return jsonify({
            "error": "A avaliação deve ser de 1 a 5."
        }), 400

    comment = str(data.get("comment", "")).strip()

    review = Review(
        contract_id=contract.id,
        client_id=contract.client_id,
        professional_id=contract.professional_id,
        rating=rating,
        comment=comment
    )

    db.session.add(review)
    db.session.flush()

    average = db.session.query(
        func.avg(Review.rating)
    ).filter(
        Review.professional_id == contract.professional_id
    ).scalar()

    professional = User.query.get(contract.professional_id)

    if professional:
        professional.rating = round(float(average or 0), 2)

    db.session.commit()

    return jsonify({
        "message": "Avaliação registada com sucesso.",
        "review": review.to_dict(),
        "professional_rating": professional.rating if professional else 0
    }), 201


@app.get("/api/reviews")
def list_all_reviews():
    reviews = Review.query.order_by(
        Review.id.desc()
    ).all()

    return jsonify([x.to_dict() for x in reviews])


@app.get("/api/reviews/client/<int:client_id>")
def list_client_reviews(client_id):
    reviews = Review.query.filter_by(
        client_id=client_id
    ).order_by(Review.id.desc()).all()

    return jsonify([x.to_dict() for x in reviews])


@app.get("/api/professionals/<int:professional_id>/reviews")
def list_professional_reviews(professional_id):
    professional = User.query.get_or_404(professional_id)

    reviews = Review.query.filter_by(
        professional_id=professional_id
    ).order_by(Review.id.desc()).all()

    average = db.session.query(
        func.avg(Review.rating)
    ).filter(
        Review.professional_id == professional_id
    ).scalar()

    return jsonify({
        "professional_id": professional.id,
        "professional_name": professional.name,
        "rating": round(float(average or 0), 2),
        "total_reviews": len(reviews),
        "reviews": [x.to_dict() for x in reviews]
    })


@app.get("/api/admin/reviews")
def admin_reviews():
    phone = request.headers.get("X-Admin-Phone", "").strip()

    user = User.query.filter_by(phone=phone).first()

    if not user or user.role not in ["admin", "team"]:
        return jsonify({
            "error": "Acesso não autorizado."
        }), 403

    reviews = Review.query.order_by(
        Review.id.desc()
    ).all()

    return jsonify([x.to_dict() for x in reviews])


@app.get("/api/admin/stats")
def admin_stats():
    session = get_company_session()

    if not session:
        return jsonify({
            "error": "Sessão empresarial inválida ou expirada."
        }), 403

    user = User.query.get(session.user_id)

    if not user or user.role not in ["admin", "team"]:
        return jsonify({
            "error": "Acesso não autorizado."
        }), 403

    total_users = User.query.count()
    total_clients = User.query.filter_by(role="client").count()
    total_professionals = User.query.filter_by(role="professional").count()

    total_requests = ServiceRequest.query.count()
    requests_open = ServiceRequest.query.filter_by(
        status="open"
    ).count()
    requests_contracted = ServiceRequest.query.filter_by(
        status="contracted"
    ).count()

    total_contracts = Contract.query.count()

    total_contract_value = db.session.query(
        func.coalesce(func.sum(Contract.price), 0)
    ).scalar()

    total_proposals = Proposal.query.count()
    total_reviews = Review.query.count()

    average_rating = db.session.query(
        func.avg(Review.rating)
    ).scalar()

    # O backend atual ainda não possui tabela própria de tickets.
    total_support_tickets = 0

    return jsonify({
        "total_users": total_users,
        "total_clients": total_clients,
        "total_professionals": total_professionals,
        "total_requests": total_requests,
        "requests_open": requests_open,
        "requests_contracted": requests_contracted,
        "total_contracts": total_contracts,
        "total_contract_value": float(total_contract_value or 0),
        "total_proposals": total_proposals,
        "total_reviews": total_reviews,
        "average_rating": round(float(average_rating or 0), 2),
        "total_support_tickets": total_support_tickets
    })


@app.get("/api/admin/monthly")
def admin_monthly():
    session = get_company_session()

    if not session:
        return jsonify({
            "error": "Sessão empresarial inválida ou expirada."
        }), 403

    user = User.query.get(session.user_id)

    if not user or user.role not in ["admin", "team"]:
        return jsonify({
            "error": "Acesso não autorizado."
        }), 403

    rows = []

    for year_month in db.session.query(
        func.strftime("%Y-%m", ServiceRequest.created_at)
    ).distinct().order_by(
        func.strftime("%Y-%m", ServiceRequest.created_at)
    ).all():

        month = year_month[0]

        requests_count = ServiceRequest.query.filter(
            func.strftime("%Y-%m", ServiceRequest.created_at) == month
        ).count()

        revenue = db.session.query(
            func.coalesce(func.sum(Contract.price), 0)
        ).filter(
            func.strftime("%Y-%m", Contract.created_at) == month
        ).scalar()

        rows.append({
            "month": month,
            "requests": requests_count,
            "revenue": float(revenue or 0)
        })

    return jsonify(rows)


@app.post("/api/support")
def create_support_ticket():
    data = request.get_json(silent=True) or {}
    required = ["name", "contact", "topic", "message"]
    missing = [
        field
        for field in required
        if not str(data.get(field, "")).strip()
    ]

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
    return jsonify(
        SupportTicket.query.get_or_404(ticket_id).to_dict()
    )


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        use_reloader=False
    )
