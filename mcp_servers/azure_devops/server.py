"""
KwikLedgers - MCP Server: Azure DevOps
Expoe ferramentas para o agente interagir com historias, PRs e sprints.
"""
import os
import asyncio
import subprocess
from datetime import datetime
from pathlib import Path
from typing import Optional

# Carrega .env automaticamente - nao precisa configurar variaveis no shell
_env_file = Path(__file__).parent.parent.parent / ".env"
if _env_file.exists():
    try:
        from dotenv import load_dotenv
        load_dotenv(_env_file)
    except ImportError:
        # fallback manual caso dotenv nao esteja instalado ainda
        for line in _env_file.read_text().splitlines():
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, _, v = line.partition("=")
                os.environ.setdefault(k.strip(), v.strip())

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent
from azure.devops.connection import Connection
from azure.devops.v7_0.work_item_tracking.models import Wiql
from msrest.authentication import BasicAuthentication


# --- Conexao com Azure DevOps ---

def get_client():
    org_url = os.environ["AZURE_ORG_URL"]
    pat = os.environ["AZURE_PAT"]
    credentials = BasicAuthentication("", pat)
    connection = Connection(base_url=org_url, creds=credentials)
    return connection


def get_project():
    return os.environ.get("AZURE_PROJECT", "KwikLedgers")


# --- Servidor MCP ---

server = Server("kwikledgers-azure-devops")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(name="get_active_user", description="Retorna o email do usuario ativo via git config"),
        Tool(name="get_user_stories", description="Lista historias do Azure DevOps atribuidas ao email informado",
             inputSchema={"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}),
        Tool(name="get_sprint_stories", description="Lista todas as historias do sprint atual do projeto"),
        Tool(name="get_story_details", description="Retorna detalhes completos de uma historia: criterios, tasks, story points",
             inputSchema={"type": "object", "properties": {"story_id": {"type": "integer"}}, "required": ["story_id"]}),
        Tool(name="get_open_prs", description="Lista PRs abertas atribuidas ao usuario",
             inputSchema={"type": "object", "properties": {"email": {"type": "string"}}, "required": ["email"]}),
        Tool(name="update_story_status", description="Atualiza o status de uma historia no Azure DevOps",
             inputSchema={"type": "object",
                          "properties": {"story_id": {"type": "integer"}, "status": {"type": "string"}},
                          "required": ["story_id", "status"]}),
        Tool(name="add_story_comment", description="Adiciona um comentario a uma historia",
             inputSchema={"type": "object",
                          "properties": {"story_id": {"type": "integer"}, "comment": {"type": "string"}},
                          "required": ["story_id", "comment"]}),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = await _dispatch(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro: {str(e)}")]


async def _dispatch(name: str, arguments: dict) -> str:
    if name == "get_active_user":
        return _get_active_user()
    if name == "get_user_stories":
        return _get_user_stories(arguments["email"])
    if name == "get_sprint_stories":
        return _get_sprint_stories()
    if name == "get_story_details":
        return _get_story_details(arguments["story_id"])
    if name == "get_open_prs":
        return _get_open_prs(arguments["email"])
    if name == "update_story_status":
        return _update_story_status(arguments["story_id"], arguments["status"])
    if name == "add_story_comment":
        return _add_story_comment(arguments["story_id"], arguments["comment"])
    return f"Ferramenta desconhecida: {name}"


# --- Implementacoes das ferramentas ---

def _get_active_user() -> str:
    """Le o email do git config local ou global."""
    try:
        result = subprocess.run(
            ["git", "config", "user.email"],
            capture_output=True, text=True, timeout=5
        )
        email = result.stdout.strip()
        if email:
            return f"Usuario ativo: {email}"
        return "Email nao configurado no git. Configure com: git config --global user.email seu@email.com"
    except Exception as e:
        return f"Nao foi possivel obter o usuario: {e}"


def _get_user_stories(email: str) -> str:
    """Busca historias atribuidas ao email no Azure DevOps."""
    connection = get_client()
    wit = connection.clients.get_work_item_tracking_client()

    query = Wiql(query=f"""
        SELECT [System.Id], [System.Title], [System.State],
               [Microsoft.VSTS.Scheduling.StoryPoints], [System.IterationPath]
        FROM WorkItems
        WHERE [System.AssignedTo] = '{email}'
          AND [System.WorkItemType] = 'User Story'
          AND [System.State] NOT IN ('Closed', 'Resolved', 'Done')
        ORDER BY [Microsoft.VSTS.Common.Priority] ASC
    """)

    result = wit.query_by_wiql(query, project=get_project())
    if not result.work_items:
        return "Nenhuma historia encontrada para este usuario."

    ids = [str(wi.id) for wi in result.work_items]
    items = wit.get_work_items(ids=ids, fields=[
        "System.Id", "System.Title", "System.State",
        "Microsoft.VSTS.Scheduling.StoryPoints", "System.IterationPath"
    ])

    lines = ["Historias atribuidas:\n"]
    for item in items:
        f = item.fields
        lines.append(
            f"KL-{f['System.Id']}: {f['System.Title']}\n"
            f"  Status: {f['System.State']} | "
            f"Story Points: {f.get('Microsoft.VSTS.Scheduling.StoryPoints', '?')} | "
            f"Sprint: {f.get('System.IterationPath', '?')}\n"
        )
    return "\n".join(lines)


def _get_sprint_stories() -> str:
    """Busca historias do sprint atual."""
    connection = get_client()
    wit = connection.clients.get_work_item_tracking_client()

    query = Wiql(query="""
        SELECT [System.Id], [System.Title], [System.State],
               [System.AssignedTo], [Microsoft.VSTS.Scheduling.StoryPoints]
        FROM WorkItems
        WHERE [System.WorkItemType] = 'User Story'
          AND [System.IterationPath] = @CurrentIteration
          AND [System.State] NOT IN ('Closed', 'Done')
        ORDER BY [Microsoft.VSTS.Common.Priority] ASC
    """)

    result = wit.query_by_wiql(query, project=get_project())
    if not result.work_items:
        return "Nenhuma historia no sprint atual."

    ids = [str(wi.id) for wi in result.work_items]
    items = wit.get_work_items(ids=ids, fields=[
        "System.Id", "System.Title", "System.State",
        "System.AssignedTo", "Microsoft.VSTS.Scheduling.StoryPoints"
    ])

    lines = ["Sprint atual:\n"]
    for item in items:
        f = item.fields
        assigned = f.get("System.AssignedTo", {})
        assigned_name = assigned.get("displayName", "Nao atribuido") if isinstance(assigned, dict) else str(assigned)
        lines.append(
            f"KL-{f['System.Id']}: {f['System.Title']}\n"
            f"  Status: {f['System.State']} | "
            f"Points: {f.get('Microsoft.VSTS.Scheduling.StoryPoints', '?')} | "
            f"Responsavel: {assigned_name}\n"
        )
    return "\n".join(lines)


def _get_story_details(story_id: int) -> str:
    """Retorna detalhes completos da historia incluindo criterios de aceite e tasks."""
    connection = get_client()
    wit = connection.clients.get_work_item_tracking_client()

    item = wit.get_work_item(id=story_id, expand="Relations", fields=[
        "System.Id", "System.Title", "System.Description", "System.State",
        "Microsoft.VSTS.Common.AcceptanceCriteria",
        "Microsoft.VSTS.Scheduling.StoryPoints",
        "Microsoft.VSTS.Common.Priority",
        "System.IterationPath", "System.AssignedTo",
        "System.Tags"
    ])

    f = item.fields
    lines = [
        f"=== KL-{story_id}: {f['System.Title']} ===",
        f"Status: {f['System.State']}",
        f"Story Points: {f.get('Microsoft.VSTS.Scheduling.StoryPoints', '?')}",
        f"Prioridade: {f.get('Microsoft.VSTS.Common.Priority', '?')}",
        f"Sprint: {f.get('System.IterationPath', '?')}",
        "",
        "Descricao:",
        f.get("System.Description", "Sem descricao"),
        "",
        "Criterios de Aceite:",
        f.get("Microsoft.VSTS.Common.AcceptanceCriteria", "Sem criterios definidos"),
        "",
    ]

    # Busca tasks filhas
    if item.relations:
        task_ids = [
            rel.url.split("/")[-1]
            for rel in item.relations
            if rel.rel == "System.LinkTypes.Hierarchy-Forward"
        ]
        if task_ids:
            tasks = wit.get_work_items(ids=task_ids, fields=[
                "System.Id", "System.Title", "System.State",
                "Microsoft.VSTS.Scheduling.RemainingWork"
            ])
            lines.append("Tasks:")
            for task in tasks:
                tf = task.fields
                lines.append(
                    f"  - [{tf['System.State']}] {tf['System.Title']} "
                    f"(horas restantes: {tf.get('Microsoft.VSTS.Scheduling.RemainingWork', '?')})"
                )

    return "\n".join(lines)


def _get_open_prs(email: str) -> str:
    """Lista PRs abertas criadas pelo usuario."""
    connection = get_client()
    git = connection.clients.get_git_client()

    repos = git.get_repositories(project=get_project())
    open_prs = []

    for repo in repos:
        prs = git.get_pull_requests(
            repository_id=repo.id,
            search_criteria={"status": "active"}
        )
        for pr in prs:
            creator_email = getattr(pr.created_by, "unique_name", "")
            if email.lower() in creator_email.lower():
                age_days = (datetime.utcnow() - pr.creation_date).days
                open_prs.append(
                    f"PR #{pr.pull_request_id}: {pr.title}\n"
                    f"  Repo: {repo.name} | Branch: {pr.source_ref_name} -> {pr.target_ref_name}\n"
                    f"  Criada ha {age_days} dias"
                )

    if not open_prs:
        return "Nenhuma PR aberta encontrada para este usuario."
    return "PRs abertas:\n\n" + "\n\n".join(open_prs)


def _update_story_status(story_id: int, status: str) -> str:
    """Atualiza o estado de uma historia."""
    connection = get_client()
    wit = connection.clients.get_work_item_tracking_client()

    patch = [{"op": "add", "path": "/fields/System.State", "value": status}]
    wit.update_work_item(document=patch, id=story_id)
    return f"Historia KL-{story_id} atualizada para: {status}"


def _add_story_comment(story_id: int, comment: str) -> str:
    """Adiciona comentario a uma historia."""
    connection = get_client()
    wit = connection.clients.get_work_item_tracking_client()

    patch = [{"op": "add", "path": "/fields/System.History", "value": comment}]
    wit.update_work_item(document=patch, id=story_id)
    return f"Comentario adicionado na historia KL-{story_id}"


# --- Entry point ---

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
