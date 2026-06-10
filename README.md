# KwikLedgers Dev Agent

Agente de desenvolvimento integrado ao VS Code que:
- Acessa o Azure DevOps para listar suas historias e PRs
- Analisa a estrutura do projeto para manter consistencia tecnica
- Implementa historias seguindo os padroes KwikLedgers (PHP/Laravel, Angular)
- Executa testes via Postman MCP e Puppeteer
- Envia notificacoes e gerencia lembretes no Windows

## Estrutura

```
agent/
  kwikledgers.agent.md           <- Definicao e regras do agente
  .vscode/
    mcp.json                     <- Configuracao dos MCP Servers (copiar para workspace)
  mcp_servers/
    azure_devops/
      server.py                  <- MCP Server: Azure DevOps
      requirements.txt
    windows_calendar/
      server.py                  <- MCP Server: Windows Calendar + Notificacoes
      requirements.txt
  .env.example                   <- Template de variaveis de ambiente
  setup.ps1                      <- Script de instalacao
```

## Instalacao

### Pre-requisitos
- Python 3.11+
- Node.js 18+
- VS Code com GitHub Copilot
- Windows com Outlook instalado (para calendario)

### Passo 1: Rodar o setup
```powershell
cd agent
.\setup.ps1
```

### Passo 2: Configurar variaveis de ambiente no Windows
```powershell
setx AZURE_ORG_URL "https://dev.azure.com/kwikledgers"
setx AZURE_PAT     "seu_personal_access_token"
setx AZURE_PROJECT "KwikLedgers"
setx POSTMAN_API_KEY "sua_api_key_postman"
```
Reinicie o terminal apos configurar.

### Passo 3: Gerar Azure Personal Access Token (PAT)
1. Acesse: https://dev.azure.com/kwikledgers/_usersSettings/tokens
2. Clique em "+ New Token"
3. Nome: KwikLedgers Dev Agent
4. Selecione permissoes:
   - Work Items: Read & Write
   - Code: Read
   - Pull Request Threads: Read & Write
5. Copie o token gerado para AZURE_PAT

### Passo 4: Gerar Postman API Key
1. Acesse: https://app.postman.com/settings/me/api-keys
2. Clique em "Generate API Key"
3. Copie para POSTMAN_API_KEY

### Passo 5: Configurar o VS Code
Copie o arquivo mcp.json para a pasta .vscode do seu workspace:
```
Kwikledgers/.vscode/mcp.json
```
Se a pasta .vscode nao existir, crie-a.

### Passo 6: Reiniciar o VS Code
Feche e reabra o VS Code para carregar os MCP Servers.

## Como Usar

Abra o Copilot Chat no VS Code (Ctrl+Alt+I) e selecione o modo agente.
Digite "@KwikLedgers Dev Agent" ou selecione o agente na lista.

### Exemplos de uso

**Inicio do dia:**
> "Quero ver minhas historias de hoje"
> "Quais sao minhas prioridades para o sprint?"

**Executar uma historia:**
> "Quero implementar a historia KL-789"
> "Implemente a KL-456 seguindo os criterios de aceite"

**Verificar prazos:**
> "Quando termina o sprint atual?"
> "Me lembra amanha as 9h sobre a historia KL-789"

**Testes:**
> "Execute os testes do Postman para o accountant_backend"
> "Verifique se o endpoint de login esta funcionando"

## Ferramentas MCP disponíveis

| MCP Server | Ferramentas |
|---|---|
| kwikledgers-azure-devops | get_active_user, get_user_stories, get_sprint_stories, get_story_details, get_open_prs, update_story_status, add_story_comment |
| postman | run_collection, run_request, get_collections |
| puppeteer | navigate, screenshot, click, fill, evaluate |
| kwikledgers-windows | send_notification, create_calendar_event, get_upcoming_deadlines, schedule_reminder |

## Solucao de Problemas

**MCP Server nao inicia:**
- Verifique se Python esta no PATH: `python --version`
- Instale dependencias: `pip install -r mcp_servers/azure_devops/requirements.txt`

**Erro de autenticacao Azure DevOps:**
- Verifique se AZURE_PAT esta configurado: `echo %AZURE_PAT%`
- Verifique se o PAT nao expirou no Azure DevOps

**Notificacoes nao aparecem:**
- Verifique se as notificacoes do Windows estao habilitadas
- Tente instalar winotify: `pip install winotify`

**Calendario nao funciona:**
- Verifique se o Outlook esta instalado e configurado
- O pywin32 precisa estar instalado: `pip install pywin32`
