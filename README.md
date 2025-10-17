# Ecommerce Recommendation System

Resumo rápido
- Serviço de recomendações em Python (FastAPI) + frontend mínimo em Vue 3 (Vite).
- Este repositório contém um esqueleto do serviço de recomendações, um frontend para testes rápidos e utilitários de debug e logging.

Status atual (resumido)
- Backend (FastAPI): esqueleto implementado com endpoints `/health`, `/api/recommendations/{user_id}` (mock) e `/debug` (HTML).
- Model: `app/models/recommendation_model.py` fornece fallback mock e interface para artefatos `joblib`.
- Frontend: scaffold Vue 3 + Vite em `frontend/` com componentes `HealthCheck` e `Recommendations`.
- Observability: logger estruturado com `structlog` e middleware de logging adicionados ao backend.

Rápido - Como rodar (PowerShell)

1) Backend (FastAPI)

```powershell
cd c:\Users\Willian Tcheldon\Repos\ecommerce-recommendation-system\python-recommendation-service
# opcional: criar/ativar venv
# python -m venv .venv; .\.venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload --port 5000
```

Endpoints úteis
- `GET /health` → health
- `GET /api/recommendations/{user_id}?limit=N` → recomendações (JSON)
- `GET /debug?user_id=1&limit=5` → página HTML para debug rápido

2) Frontend (Vue + Vite)

```powershell
cd c:\Users\Willian Tcheldon\Repos\ecommerce-recommendation-system\frontend
npm install
npm run dev
# abre o navegador no endereço mostrado pelo vite (por padrão http://localhost:5173)
```

Observações práticas
- O `vite.config.js` já contém proxy para `/api` e `/health` apontando para `http://localhost:5000` (modo dev), para evitar problemas de CORS.
- Para produção, gere o build (`npm run build`) e sirva os assets com um servidor estático ou integre ao backend.

Debug e logs
- Página de debug: abra `http://localhost:5000/debug?user_id=123&limit=5` para ver o resultado da recomendação formatado em HTML.
- Logs estruturados: o backend usa `structlog` para emitir logs JSON. Verifique o console onde uvicorn roda para visualizar entradas de log.

Execução local rápida (checklist)
1. Subir backend
2. Abrir debug: http://localhost:5000/debug
3. Subir frontend (opcional) e testar a UI

Arquitetura resumida
- `python-recommendation-service/` - serviço FastAPI (modelo de recomendação, rotas, debug, logging)
- `frontend/` - app Vue 3 + Vite (dev UI para testar recomendações)
- `docker-compose.yml` - orquestração proposta (postgres, redis, services) — arquivo criado porém não totalmente integrado com serviços completos

Próximos passos recomendados
- Instalar dependências e confirmar que testes passam (`pytest`).
- Implementar engine real em `recommendation_engine.py` e integrar ao `RecommendationModel`.
- Adicionar métricas (Prometheus) e tracing (OpenTelemetry) para observability completa.
- Completar documentação de API (OpenAPI / Swagger já exposto pelo FastAPI) e exemplos de uso.

Contribuição
- Leia a `IMPLEMENTATION.md` para um resumo de implementação e o status de tarefas.
