# Contributing

## English

### Scope

This repository owns the KwikLedgers Copilot agent contract, MCP servers,
shared runtime setup, and agent-facing operational documentation.

Issues that belong to product application code under `projects/` should be
opened in the relevant product repository.

### First Steps

1. Read `README.md` and the MCP server folders before changing behavior.
2. Confirm whether the change belongs in agent configuration, Azure DevOps
   integration, local tracking, or Windows notifications.
3. Keep setup, environment discovery, and MCP behavior aligned.
4. When this repository is edited from the workspace root, also append the root
   history file in `../docs/history/`.

### Pull Request Expectations

- Describe the workflow impact.
- Validate the smallest affected slice first.
- Update docs when prompts, setup, or MCP tools change.
- Avoid product-repo architecture changes from this repository.

## Portugues

### Escopo

Este repositorio cuida do contrato do agente Copilot da KwikLedgers, dos MCP
servers, do setup do runtime compartilhado e da documentacao operacional
voltada ao agente.

Issues que pertencem ao codigo de aplicacao em `projects/` devem ser abertas no
repositorio de produto relevante.

### Primeiros Passos

1. Leia `README.md` e as pastas dos MCP servers antes de mudar o
   comportamento.
2. Confirme se a mudanca pertence a configuracao do agente, a integracao com
   Azure DevOps, ao tracking local ou as notificacoes Windows.
3. Mantenha alinhados setup, descoberta de ambiente e comportamento MCP.
4. Quando este repositorio for editado a partir da raiz do workspace, adicione
   tambem o registro na history raiz em `../docs/history/`.

### Expectativas Para Pull Request

- Descreva o impacto no fluxo.
- Valide primeiro o menor trecho afetado.
- Atualize a documentacao quando prompts, setup ou ferramentas MCP mudarem.
- Evite mudancas de arquitetura de repositorios de produto a partir deste
  repositorio.