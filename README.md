# KwikLedgers Dev Agent

Agente de desenvolvimento integrado ao VS Code que:
- Acessa o Azure DevOps para listar suas historias e PRs
- Analisa a estrutura do projeto para manter consistencia tecnica
- Implementa historias seguindo os padroes KwikLedgers (PHP/Laravel, Angular)
- Executa testes via Postman MCP e Puppeteer
- Envia notificacoes e gerencia lembretes no Windows (inclusive via WSL)

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
AZURE_PROJECT=Kwik Ledgers
POSTMAN_API_KEY=sua_api_key_postman
```

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
setx AZURE_PROJECT   "Kwik Ledgers"
setx POSTMAN_API_KEY "sua_api_key_postman"
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

## Gerando a Postman API Key

1. Acesse: https://app.postman.com/settings/me/api-keys
2. "+ Generate API Key"
3. Copie para POSTMAN_API_KEY

---

## Como Usar

Abra o Copilot Chat (Ctrl+Alt+I), selecione o agente KwikLedgers Dev Agent e fale:

| O que voce quer | O que dizer |
|---|---|
| Ver historias do sprint | "Quais sao minhas historias do sprint?" |
| Implementar uma historia | "Quero implementar a historia KL-789" |
| Ver PRs abertas | "Tenho alguma PR aberta?" |
| Ver prazos | "Quando termina o sprint atual?" |
| Criar lembrete | "Me lembra amanha as 9h sobre a KL-456" |
| Rodar testes | "Execute os testes do Postman para o accountant_backend" |

## Ferramentas MCP disponíveis

| MCP Server | Ferramentas |
|---|---|
| kwikledgers-azure-devops | get_active_user, get_user_stories, get_sprint_stories, get_story_details, get_open_prs, update_story_status, add_story_comment |
| postman | run_collection, run_request, get_collections |
| puppeteer | navigate, screenshot, click, fill, evaluate |
| kwikledgers-windows | send_notification, create_calendar_event, get_upcoming_deadlines, schedule_reminder |

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

**Notificacoes nao aparecem no WSL:**
- Verifique se o powershell.exe esta acessivel: `which powershell.exe`
- Se nao estiver, instale o PowerShell para WSL ou habilite nas configuracoes do Windows

**Calendario nao funciona:**
- Verifique se o Outlook esta aberto no Windows
- O acesso ao Outlook via WSL usa COM automation pelo powershell.exe do host
