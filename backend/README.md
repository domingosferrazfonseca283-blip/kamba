# Kamba API

Backend inicial do marketplace Kamba.

## Rodar no Termux

cd backend
python -m pip install -r requirements.txt
python app.py

API:
GET /api/health
GET /api/services
GET /api/requests
POST /api/requests
POST /api/proposals
POST /api/contracts
GET /api/contracts/<id>

A base de dados SQLite é criada automaticamente em `instance/kamba.db`.
