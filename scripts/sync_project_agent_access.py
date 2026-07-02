#!/usr/bin/env python3
from __future__ import annotations

import json
from pathlib import Path


MANAGED_AGENT_MARKER = "<!-- Managed by KwikLedgers Dev Agent Setup -->"
PROJECT_AGENT_PATH = Path(".github/agents/kwikledgers-dev.agent.md")
PROJECT_COPILOT_INSTRUCTIONS_PATH = Path(".github/copilot-instructions.md")
PROJECT_MCP_PATH = Path(".vscode/mcp.json")
PROJECT_GITIGNORE_PATH = Path(".gitignore")
EXPECTED_SERVER_NAMES = (
    "kwikledgers-azure-devops",
    "kwikledgers-local-tracking",
    "kwikledgers-windows",
)
MANAGED_GITIGNORE_BLOCK = "# kwikledgers-shared-agent\n.vscode/mcp.json\n.github/agents/kwikledgers-dev.agent.md\n.github/copilot-instructions.md\n"


def build_project_mcp_payload() -> dict:
    agent_prefix = "${workspaceFolder}/../../agent/mcp_servers"
    return {
        "servers": {
            "kwikledgers-azure-devops": {
                "type": "stdio",
                "command": "bash",
                "args": [f"{agent_prefix}/azure_devops/run.sh"],
            },
            "kwikledgers-local-tracking": {
                "type": "stdio",
                "command": "bash",
                "args": [f"{agent_prefix}/local_tracking/run.sh"],
            },
            "kwikledgers-windows": {
                "type": "stdio",
                "command": "bash",
                "args": [f"{agent_prefix}/windows_calendar/run.sh"],
            },
        },
        "mcpServers": {
            "kwikledgers-azure-devops": {
                "command": "bash",
                "args": [f"{agent_prefix}/azure_devops/run.sh"],
            },
            "kwikledgers-local-tracking": {
                "command": "bash",
                "args": [f"{agent_prefix}/local_tracking/run.sh"],
            },
            "kwikledgers-windows": {
                "command": "bash",
                "args": [f"{agent_prefix}/windows_calendar/run.sh"],
            },
        },
    }


def is_git_repo(path: Path) -> bool:
    return (path / ".git").exists()


def is_managed_mcp_file(path: Path) -> bool:
    if not path.exists():
        return True

    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return False

    for group_name in ("servers", "mcpServers"):
        group = payload.get(group_name)
        if not isinstance(group, dict):
            return False

        for server_name in EXPECTED_SERVER_NAMES:
            server = group.get(server_name)
            if not isinstance(server, dict):
                return False

            args = server.get("args")
            if not isinstance(args, list) or len(args) != 1:
                return False

            arg_value = str(args[0])
            if "${workspaceFolder}/../../agent/mcp_servers/" not in arg_value:
                return False

    return True


def build_project_agent_content(root_agent_content: str) -> str:
    content = root_agent_content
    content = content.replace(
        "- Use `agent/kwikledgers.agent.md` as the detailed operating contract.",
        "- Use the shared workspace contract at `../../agent/kwikledgers.agent.md` as the detailed operating contract.",
    )
    content = content.replace(
        "- Follow `.github/copilot-instructions.md` and `AGENTS.md` for workspace rules.",
        "- Follow the shared workspace rules at `../../.github/copilot-instructions.md` and `../../AGENTS.md`.",
    )
    return f"{MANAGED_AGENT_MARKER}\n{content}"


def build_project_copilot_instructions(root_instructions: str) -> str:
    content = root_instructions
    content = content.replace(
        "Use `agent/kwikledgers.agent.md` as the primary agent contract for this\nworkspace.",
        "Use `../../agent/kwikledgers.agent.md` as the primary agent contract for this\nrepository.",
    )
    content = content.replace(
        "- Every repository change made by the agent must be documented in\n  `docs/history/kwikledgers-alteration-YYYY-MM-DD.md`.",
        "- Repository changes made inside this project repository should follow the\n  target repository workflow first; workspace-level audit history still lives at\n  `../../docs/history/kwikledgers-alteration-YYYY-MM-DD.md` when changes are\n  coordinated from the workspace root.",
    )
    content = content.replace(
        "Current history file pattern:",
        "Current workspace history file pattern:",
    )
    content = content.replace(
        "- `docs/history/kwikledgers-alteration-2026-07-01.md`",
        "- `../../docs/history/kwikledgers-alteration-2026-07-01.md`",
    )
    return f"{MANAGED_AGENT_MARKER}\n{content}"


def is_managed_agent_file(path: Path) -> bool:
    if not path.exists():
        return True
    try:
        return path.read_text(encoding="utf-8").startswith(MANAGED_AGENT_MARKER)
    except Exception:
        return False


def ensure_gitignore_rules(project_repo: Path) -> str:
    gitignore_path = project_repo / PROJECT_GITIGNORE_PATH
    existing = gitignore_path.read_text(encoding="utf-8") if gitignore_path.exists() else ""

    if MANAGED_GITIGNORE_BLOCK.strip() in existing:
        return "gitignore"

    new_content = existing
    if new_content and not new_content.endswith("\n"):
        new_content += "\n"
    new_content += "\n" + MANAGED_GITIGNORE_BLOCK
    gitignore_path.write_text(new_content, encoding="utf-8")
    return "gitignore"


def sync_project_repo(project_repo: Path, root_agent_content: str, root_instructions: str) -> list[str]:
    messages: list[str] = []

    mcp_path = project_repo / PROJECT_MCP_PATH
    mcp_path.parent.mkdir(parents=True, exist_ok=True)
    if is_managed_mcp_file(mcp_path):
        mcp_path.write_text(
            json.dumps(build_project_mcp_payload(), indent=2, ensure_ascii=True) + "\n",
            encoding="utf-8",
        )
        messages.append("mcp")
    else:
        messages.append("mcp-skipped")

    agent_path = project_repo / PROJECT_AGENT_PATH
    agent_path.parent.mkdir(parents=True, exist_ok=True)
    if is_managed_agent_file(agent_path):
        agent_path.write_text(build_project_agent_content(root_agent_content), encoding="utf-8")
        messages.append("agent")
    else:
        messages.append("agent-skipped")

    instructions_path = project_repo / PROJECT_COPILOT_INSTRUCTIONS_PATH
    instructions_path.parent.mkdir(parents=True, exist_ok=True)
    if is_managed_agent_file(instructions_path):
        instructions_path.write_text(build_project_copilot_instructions(root_instructions), encoding="utf-8")
        messages.append("instructions")
    else:
        messages.append("instructions-skipped")

    messages.append(ensure_gitignore_rules(project_repo))

    return messages


def main() -> int:
    script_dir = Path(__file__).resolve().parent
    agent_dir = script_dir.parent
    workspace_root = agent_dir.parent
    projects_dir = workspace_root / "projects"
    root_agent_path = workspace_root / ".github/agents/kwikledgers-dev.agent.md"
    root_instructions_path = workspace_root / ".github/copilot-instructions.md"
    root_agent_content = root_agent_path.read_text(encoding="utf-8")
    root_instructions = root_instructions_path.read_text(encoding="utf-8")

    if not projects_dir.exists():
        print("Nenhuma pasta projects/ encontrada; nada para sincronizar.")
        return 0

    synced_repos = 0
    skipped_repos: list[str] = []

    for project_repo in sorted(projects_dir.iterdir()):
        if not project_repo.is_dir() or project_repo.name == "documentacao":
            continue
        if not is_git_repo(project_repo):
            continue

        actions = sync_project_repo(project_repo, root_agent_content, root_instructions)
        synced_repos += 1
        if any(action.endswith("skipped") for action in actions):
            skipped_repos.append(f"{project_repo.name}: {', '.join(actions)}")
        else:
            print(f"Sincronizado: {project_repo}")

    print(f"Repositorios de projeto sincronizados: {synced_repos}")
    if skipped_repos:
        print("Repositorios com arquivos locais preservados:")
        for skipped_repo in skipped_repos:
            print(f"- {skipped_repo}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())