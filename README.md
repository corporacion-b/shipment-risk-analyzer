# shipment-risk-analyzer

<p align="center">
  API de análisis de riesgo en envíos construida con FastAPI.
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.10+-3776AB?style=for-the-badge&logo=python&logoColor=white" alt="Python">
  <img src="https://img.shields.io/badge/FastAPI-API-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/Pytest-Tests-0A9EDC?style=for-the-badge&logo=pytest&logoColor=white" alt="Pytest">
  <img src="https://img.shields.io/badge/Docker-Containerized-2496ED?style=for-the-badge&logo=docker&logoColor=white" alt="Docker">
</p>

Servicio de análisis de riesgo del sistema Shipment Tracker. Consulte [corporacion-b/.github](https://github.com/corporacion-b/.github) para la descripción completa del proyecto y las instrucciones de ejecución con Docker Compose.

---

## Requisitos previos

- Docker y Docker Compose
- Los tres repositorios clonados en la carpeta raíz del proyecto (ver [corporacion-b/.github](https://github.com/corporacion-b/.github))

---

## Ejecución

Este servicio se levanta junto con el resto del sistema desde la carpeta raíz del proyecto:

```bash
cp .env.example .env
docker compose up --build
```

Las variables de entorno se configuran en el `.env` de la raíz. La API queda disponible en `http://localhost:8002`.

---

## Endpoints

| Método | Endpoint | Descripción |
| --- | --- | --- |
| GET | `/tracking/alerts` | Lista notificaciones del usuario |
| POST | `/tracking/evaluate` | Evalúa automáticamente un refresh de shipment |
| PATCH | `/tracking/alerts/{alert_id}` | Actualiza el estado de una alerta |
| POST | `/tracking/alerts/mark-read` | Marca alertas como leídas |
| DELETE | `/tracking/alerts/{alert_id}` | Elimina una alerta |
| DELETE | `/tracking/alerts/by-shipment/{tracking_id}` | Elimina todas las alertas de un envío |

Documentación automática: `http://localhost:8002/docs`

---

## Pruebas

```bash
pytest
```

Las pruebas que tocan base de datos requieren MySQL disponible.
