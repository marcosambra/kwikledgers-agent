# KwikLedgers Dev Agent

Repository name: `kwikledgers-agent`

Folder: `/home/ambra/Kwikledgers/agent`

Description: Azure DevOps-focused Copilot agent repository for daily sprint follow-up, local AI tracking, MCP integration, and implementation guidance across KwikLedgers projects.

Agente de desenvolvimento integrado ao VS Code que:
- Acessa o Azure DevOps para listar historias, tasks, bugs e PRs do usuario ativo
- Gera arquivos locais de controle do sprint, log diario e metricas de IA
- Destaca bloqueios, itens devolvidos por mudanca de estado e story points restantes
- Analisa a estrutura do projeto para manter consistencia tecnica quando os repositorios estiverem em `projects/`
- Envia notificacoes e gerencia lembretes no Windows (inclusive via WSL)

## English

### First Steps

1. Run `setup.sh` on Linux or WSL, or `setup.ps1` on Windows.
2. Fill the `.env` file with Azure DevOps credentials and project settings.
3. Open the workspace in VS Code and allow the MCP servers.
4. Select `KwikLedgers Dev Agent` in Copilot Chat.
5. Start with a daily summary and a local tracking sync.

### How To Use

Use this repository when you need the agent runtime itself, not product
application code.

Typical prompts:

- `Show my daily Azure summary.`
- `Update my local sprint tracking files.`
- `Do I have blocked or returned items?`
- `Register today's AI usage metrics.`

### Repository Guides

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [Bug report template](.github/ISSUE_TEMPLATE/bug_report.md)
- [Feature request template](.github/ISSUE_TEMPLATE/feature_request.md)
- [Documentation update template](.github/ISSUE_TEMPLATE/documentation_update.md)

## Recommended License Structure

For internal company use, the recommended structure is:

```text
LICENSE.md
README.md
CONTRIBUTING.md
```

Suggested license label:

- `Proprietary - Internal Use Only`

## Estrutura

```
agent/
  kwikledgers.agent.md           <- Definicao e regras do agente
  .vscode/
    mcp.json                     <- Configuracao dos MCP Servers
  mcp_servers/
    azure_devops/
      server.py                  <- MCP Server: Azure DevOps
      requirements.txt
    local_tracking/
      server.py                  <- MCP Server: gera AI_Tracking/
      requirements.txt
    windows_calendar/
      server.py                  <- MCP Server: Windows Calendar + Notificacoes
      requirements.txt
  .env.example                   <- Template de variaveis de ambiente
  setup.sh                       <- Script de instalacao para Linux/WSL
  setup.ps1                      <- Script de instalacao para Windows (PowerShell)
  README.md
```

## Instalacao

### Pre-requisitos
- Python 3.11+
- Node.js 18+
- VS Code com GitHub Copilot
- Outlook instalado no Windows (para calendario e notificacoes)

---

### Instalacao no WSL (recomendado para a equipe KwikLedgers)

#### Passo 1: Clonar o repositorio dentro do WSL
```bash
cd ~
git clone https://viwaredevops@dev.azure.com/viwaredevops/Kwik%20Ledgers/_git/kwikledgers-dev-agent agent
cd agent
```

#### Passo 2: Rodar o setup
```bash
chmod +x setup.sh
./setup.sh
```

#### Passo 3: Preencher as credenciais
O setup.sh cria o arquivo `.env` automaticamente. Edite-o:
```bash
nano .env
```
Preencha os valores:
```
AZURE_ORG_URL=https://dev.azure.com/viwaredevops
AZURE_PAT=seu_personal_access_token
AZURE_USER_EMAIL=seu_email@empresa.com
AZURE_PROJECT=Kwik Ledgers
```

Os MCP servers procuram `.env` automaticamente subindo pela arvore de diretorios.
Isso permite separar `azure_devops/`, `local_tracking/` e `windows_calendar/` em submodulos Git sem quebrar a descoberta de configuracao.
Se quiser apontar explicitamente para outro arquivo, defina `KWIKLEDGERS_ENV_FILE` ou `MCP_ENV_FILE`.

#### Passo 4: Recarregar o shell
```bash
source ~/.bashrc   # ou source ~/.zshrc
```

#### Passo 5: Copiar o mcp.json para o workspace
```bash
mkdir -p /home/seu_usuario/Kwikledgers/.vscode
cp .vscode/mcp.json /home/seu_usuario/Kwikledgers/.vscode/mcp.json
```

#### Passo 6: Reiniciar o VS Code e usar
- Abra o Copilot Chat: Ctrl+Alt+I
- Selecione o agente: KwikLedgers Dev Agent
- Na primeira vez, clique em Allow em cada MCP Server

---

### Instalacao no Windows (PowerShell)

#### Passo 1: Clonar
```powershell
git clone https://viwaredevops@dev.azure.com/viwaredevops/Kwik%20Ledgers/_git/kwikledgers-dev-agent agent
cd agent
```

#### Passo 2: Setup
```powershell
.\setup.ps1
```

#### Passo 3: Variaveis de ambiente
```powershell
setx AZURE_ORG_URL   "https://dev.azure.com/viwaredevops"
setx AZURE_PAT       "seu_personal_access_token"
setx AZURE_USER_EMAIL "seu_email@empresa.com"
setx AZURE_PROJECT   "Kwik Ledgers"
```
Reinicie o terminal apos configurar.

---

## Gerando o Azure Personal Access Token (PAT)

1. Acesse: https://dev.azure.com/viwaredevops/_usersSettings/tokens
2. Clique em "+ New Token"
3. Nome: KwikLedgers Dev Agent
4. Expiracao: 1 ano
5. Permissoes:
   - Work Items: Read & Write
   - Code: Read
   - Pull Request Threads: Read & Write
6. Copie o token gerado para AZURE_PAT

## Primeiros Passos

1. Rode `setup.sh` no Linux ou WSL, ou `setup.ps1` no Windows.
2. Preencha o arquivo `.env` com as credenciais do Azure DevOps e as
  configuracoes do projeto.
3. Abra o workspace no VS Code e autorize os MCP servers.
4. Selecione `KwikLedgers Dev Agent` no Copilot Chat.
5. Comece com o resumo diario e a sincronizacao do tracking local.

## Guias Do Repositorio

- [CONTRIBUTING.md](CONTRIBUTING.md)
- [SECURITY.md](SECURITY.md)
- [Template de bug](.github/ISSUE_TEMPLATE/bug_report.md)
- [Template de funcionalidade](.github/ISSUE_TEMPLATE/feature_request.md)
- [Template de documentacao](.github/ISSUE_TEMPLATE/documentation_update.md)

## Como Usar

Abra o Copilot Chat (Ctrl+Alt+I), selecione o agente KwikLedgers Dev Agent e fale:

| O que voce quer | O que dizer |
|---|---|
| Ver resumo do sprint | "Quais sao minhas tasks e historias do sprint atual?" |
| Ver itens bloqueados | "Tenho algum item bloqueado no sprint atual?" |
| Gerar controle local | "Atualize meus arquivos de controle do sprint em AI_Tracking." |
| Registrar atividade diaria | "Registre no log diario que revisei a KL-456 e atualizei seu status." |
| Registrar metricas | "Registre as metricas operacionais de IA desta revisao." |
| Implementar uma historia | "Quero implementar a historia KL-789" |
| Ver PRs abertas | "Tenho alguma PR aberta?" |
| Ver prazos | "Quando termina o sprint atual?" |
| Criar lembrete | "Me lembra amanha as 9h sobre a KL-456" |

## Primeiro Fluxo Recomendado

Depois de configurar o `.env` e permitir os MCP servers no VS Code, use esta sequencia para iniciar o trabalho com o agente:

1. "Quais sao minhas tasks e historias do sprint atual?"
2. "Atualize meus arquivos de controle do sprint em AI_Tracking."
3. "Tenho algum item bloqueado ou devolvido para mim?"
4. "Quero implementar a historia KL-XXX" ou "Quero trabalhar na task KL-XXX"

Ao clonar os repositorios em `projects/`, abra o projeto alvo no workspace e mantenha esse mesmo fluxo: resumo do sprint, sincronizacao do tracking e depois implementacao.

## Estrutura com Submodulos

Se voce separar os MCP servers em submodulos Git dentro de `agent/mcp_servers/`, mantenha esta estrutura:

```text
agent/
  .env
  mcp_servers/
    azure_devops/      <- pode ser submodulo
    local_tracking/    <- pode ser submodulo
    windows_calendar/  <- pode ser submodulo
    utils/
```

Com isso, cada servidor encontra automaticamente o `.env` do `agent/` ou um caminho explicitamente configurado.

## Ferramentas MCP disponíveis

| MCP Server | Ferramentas |
|---|---|
| kwikledgers-azure-devops | get_active_user, get_my_work_items, get_my_blocked_items, get_my_daily_summary, get_user_stories, get_sprint_stories, get_story_details, get_open_prs, update_story_status, add_story_comment |
| kwikledgers-local-tracking | sync_daily_tracking, update_task_control, append_daily_action_log, record_ai_metrics, read_tracking_snapshot |
| kwikledgers-windows | send_notification, create_calendar_event, get_upcoming_deadlines, schedule_reminder |

## Saidas Locais

O agente passa a gerar arquivos em `AI_Tracking/` na raiz do workspace:

- `AI_Tracking/Task_Control/current-sprint.json`
- `AI_Tracking/Task_Control/current-sprint.md`
- `AI_Tracking/Daily_Action_Logs/YYYY-MM-DD.md`
- `AI_Tracking/Metrics/ai-usage-log.md`
- `AI_Tracking/Metrics/sprint-metrics.md`

## Solucao de Problemas

**MCP Server nao inicia:**
```bash
python3 -c "import mcp; print('ok')"
pip3 install -r mcp_servers/azure_devops/requirements.txt
```

**Erro de autenticacao Azure DevOps:**
```bash
echo $AZURE_PAT   # deve imprimir o token
```
Se vazio: `source ~/.bashrc` e tente novamente.

**Resumo nao encontra items do usuario:**
```bash
echo $AZURE_USER_EMAIL
git config --global user.email
```
Defina `AZURE_USER_EMAIL` se o email do Azure DevOps nao for o mesmo do git.

**Logs de auditoria muito detalhados:**
- O agente grava auditoria em `AI_Tracking/Audit/mcp-audit.log`.
- Resumos grandes do Azure sao compactados para manter apenas contagens e IDs principais.

**Notificacoes nao aparecem no WSL:**
- Verifique se o powershell.exe esta acessivel: `which powershell.exe`
- Se nao estiver, instale o PowerShell para WSL ou habilite nas configuracoes do Windows

**Calendario nao funciona:**
- Verifique se o Outlook esta aberto no Windows
- O acesso ao Outlook via WSL usa COM automation pelo powershell.exe do host
