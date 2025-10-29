# Estratégia de Treinamento dos Modelos de Recomendação

## Como Funciona

### 1. **Treinamento Automático (Recomendado)**
   - **Frequência**: Diariamente via Celery Beat
   - **Quando**: Às 00:00 UTC (configurável em `tasks/celery_app.py`)
   - **Vantagem**: Automático, sem intervenção manual
   - **Requisito**: Celery worker e beat devem estar rodando

### 2. **Treinamento Manual via API**
   - **Endpoint**: `POST /api/v1/recommendations/train`
   - **Acesso**: Apenas administradores
   - **Quando usar**: 
     - Primeira vez (não há modelos treinados)
     - Quando adicionar muitos livros de uma vez
     - Para forçar retreinamento imediato

### 3. **Treinamento na Inicialização (Opcional)**
   - **Como ativar**: Definir variável de ambiente `AUTO_TRAIN_ON_STARTUP=true`
   - **Comportamento**: Treina automaticamente na inicialização SE os modelos não existirem
   - **Quando usar**: Primeira vez ou após limpar os modelos

## ❌ O que NÃO fazer

**NÃO treine o modelo a cada interação** (ex: quando adicionar ao carrinho):
- O treinamento é pesado (processa TODOS os dados do banco)
- Pode demorar vários minutos dependendo do volume
- Travaria a aplicação para cada usuário
- As interações já são salvas no banco e serão usadas no próximo treinamento

## ✅ Estratégia Recomendada

### Para Produção:
1. **Deixar Celery rodar** - treinamento diário automático
2. **Treinar manualmente** apenas quando necessário (grandes atualizações de catálogo)

### Para Desenvolvimento:
1. **Primeira vez**: `POST /api/v1/recommendations/train` ou `AUTO_TRAIN_ON_STARTUP=true`
2. **Depois**: Deixar o Celery gerenciar ou treinar manualmente quando necessário

## Fluxo de Dados

```
Interação do Usuário (Carrinho, View, etc.)
    ↓
Salva no Banco (UserInteraction)
    ↓
Aguardando até próximo treinamento
    ↓
Celery treina diariamente (lê TODAS as interações)
    ↓
Modelos atualizados
    ↓
Recomendações melhoradas
```

## Performance

- **Treinamento completo**: Pode levar de 1-10 minutos dependendo do volume
- **Impacto**: O modelo usa TODOS os dados do banco (não é incremental)
- **Frequência ideal**: Diária ou semanal para produção
- **Em produção**: Use Celery para não bloquear a aplicação

## Configuração

### Docker Compose
Certifique-se de que os serviços Celery estão rodando:
- `celery_worker`: Processa tarefas
- `celery_beat`: Agenda treinamentos periódicos

### Variáveis de Ambiente
```bash
# Treinar automaticamente na inicialização (apenas se modelos não existirem)
AUTO_TRAIN_ON_STARTUP=false  # ou true para ativar
```

### Frequência de Treinamento
Edite `tasks/celery_app.py`:
```python
'retrain-recommendation-models': {
    'task': 'tasks.recommendation_tasks.retrain_models',
    'schedule': 86400.0,  # 24 horas em segundos
}
```

## Resumo

| Quando Treinar | Método | Frequência |
|---------------|--------|------------|
| **Automático** | Celery Beat | Diariamente |
| **Manual** | API `/train` | Quando necessário |
| **Inicialização** | `AUTO_TRAIN_ON_STARTUP` | Primeira vez |
| **Nunca** | A cada interação | ❌ Não recomendado |

