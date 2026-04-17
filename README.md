#  shipment-risk-analyzer-api

##  Descripción

API desarrollada con FastAPI que analiza riesgos en envíos a partir de datos obtenidos del shipment-tracker-api. Identifica posibles retrasos, retenciones aduanales o incidencias, y genera alertas basadas en reglas de negocio.

---

##  Objetivo

Su propósito es evaluar el riesgo de un envío usando eventos históricos y condiciones externas.

---

##  Arquitectura del servicio



---

##  Stack tecnológico

* Python
* FastAPI
* PyTest
* MySQL
* Alembic
* Docker
* GitHub Actions

---

##  Estructura del proyecto

```
shipment-risk-analyzer-api/
├── .github/
│   └── workflows/
│       └── ci.yml
├── src/                     
├── tests/                   
├── Dockerfile
├── docker-compose.yml
├── .env.example              
├── .gitignore                
├── README.md
└── APRENDIZAJES.md
```

---

##  Requisitos previos

* Python 3.x
* Docker
* Acceso a shipment-tracker-api

---

##  Variables de entorno



---

##  Ejecución local

```
git clone https://github.com/corporacion-b/shipment-risk-analyzer.git
cd shipment-risk-analyzer
pip install -r requirements.txt
uvicorn src.main:src --reload
```

---

##  Docker

```
docker compose up --build
```

---

##  Endpoints

| Método | Endpoint                   | Descripción              |
| ------ | -------------------------- | ------------------------ |
| GET    | /risk/{id}/customs-hold    | Retención en aduana      |
| GET    | /risk/{id}/delay-detection | Detección de retrasos    |
| GET    | /risk/{id}/holiday-impact  | Impacto de días festivos |

---

##  Ejemplos de request/response



---

##  Documentación automática

* Swagger UI: /docs
* ReDoc: /redoc

---

##  Pruebas



---

##  CI/CD



---

##  Estrategia de ramas

* main
* develop
* feature/*
* fix/*

---

##  Integrantes

| Rol       | Nombre           |
| --------- | ---------------- |
| Tech Lead | Enrique Vidó     |
| Backend   | Josué Rosaldo    |
| QA/DevOps | Erick Rodríguez  |
| Docs      | María Montserrat |

---
