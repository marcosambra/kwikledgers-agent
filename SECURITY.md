# Security Policy

## English

### Scope

This policy covers the agent contract, MCP server code, setup scripts,
environment discovery, and operational logging inside this repository.

### Reporting

Do not open normal issues for sensitive disclosures such as Azure PAT leaks,
credential exposure, unsafe work-item mutation, or exploitable MCP behavior.

Use the team's private internal security or incident channel and include:

- affected file or MCP server
- risk description
- reproduction steps
- mitigation or rollback notes if available

### Sensitive Areas

- `.env` and `.env.example`
- `mcp_servers/azure_devops/`
- `mcp_servers/local_tracking/`
- `mcp_servers/windows_calendar/`
- audit output and environment discovery utilities

## Portugues

### Escopo

Esta politica cobre o contrato do agente, o codigo dos MCP servers, os scripts
de setup, a descoberta de ambiente e o logging operacional dentro deste
repositorio.

### Reporte

Nao abra issues normais para divulgacoes sensiveis, como vazamento de Azure
PAT, exposicao de credenciais, mutacao insegura de work items ou comportamento
MCP exploravel.

Use o canal interno e privado de seguranca ou incidentes da equipe e inclua:

- arquivo ou MCP server afetado
- descricao do risco
- passos de reproducao
- observacoes de mitigacao ou rollback, se existirem

### Areas Sensiveis

- `.env` e `.env.example`
- `mcp_servers/azure_devops/`
- `mcp_servers/local_tracking/`
- `mcp_servers/windows_calendar/`
- saida de auditoria e utilitarios de descoberta de ambiente