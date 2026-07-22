"""Executa o resumo diario completo para uso manual ou via agendador."""

import argparse
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
AGENT_DIR = SCRIPT_DIR.parent
MCP_DIR = AGENT_DIR / "mcp_servers"

sys.path.insert(0, str(MCP_DIR))

from azure_devops import server as azure_server
from local_tracking import server as tracking_server
from windows_calendar import server as windows_server


DEFAULT_ACTIONS = [
    "scheduled_daily_summary",
    "azure_daily_summary",
    "local_tracking_sync",
    "windows_notification",
]


def _build_identity_context_message(payload: dict[str, Any]) -> str:
    identity_context = payload.get("user_identity_context", {})
    email = identity_context.get("resolved_email") or payload.get("user_email") or "usuario-desconhecido"
    source = identity_context.get("email_source") or "origem-desconhecida"
    env_file_path = identity_context.get("env_file_path")
    if env_file_path:
        return f"Identidade resolvida: {email} via {source} ({env_file_path})."
    return f"Identidade resolvida: {email} via {source}."


def _parse_summary(summary_text: str) -> dict[str, Any]:
    try:
        payload = json.loads(summary_text)
    except json.JSONDecodeError as error:
        raise RuntimeError(summary_text) from error

    if not isinstance(payload, dict):
        raise RuntimeError("Resumo diario retornou payload invalido.")
    return payload


def _build_notification_message(payload: dict[str, Any]) -> str:
    counts = payload.get("counts", {})
    remaining_story_points = payload.get("remaining_story_points", "-")
    assigned_items = counts.get("assigned_items", 0)
    blocked_items = counts.get("blocked_items", 0)
    open_prs = counts.get("open_prs", 0)
    return (
        "Resumo diario sincronizado. "
        f"Itens atribuidos: {assigned_items}. "
        f"Bloqueados: {blocked_items}. "
        f"PRs abertas: {open_prs}. "
        f"Story points restantes: {remaining_story_points}. "
        f"{_build_identity_context_message(payload)}"
    )


def run_daily_summary(source: str = "task-scheduler", notify: bool = True) -> dict[str, Any]:
    summary_text = azure_server._get_my_daily_summary()
    payload = _parse_summary(summary_text)

    tracking_result = tracking_server._sync_daily_tracking(
        summary_text,
        DEFAULT_ACTIONS,
        "Resumo diario agendado",
        None,
        "Resumo diario agendado",
        None,
        source,
    )

    notification_result = None
    if notify:
        urgency = "high" if payload.get("counts", {}).get("blocked_items", 0) else "normal"
        notification_result = windows_server._send_notification(
            "Resumo diario disponivel",
            _build_notification_message(payload),
            urgency,
        )

    return {
        "summary": payload,
        "tracking_result": tracking_result,
        "notification_result": notification_result,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Executa o resumo diario do KwikLedgers.")
    parser.add_argument("--source", default="task-scheduler", help="Origem registrada no tracking local.")
    parser.add_argument(
        "--skip-notification",
        action="store_true",
        help="Nao envia notificacao Windows ao final da execucao.",
    )
    parser.add_argument(
        "--print-summary",
        action="store_true",
        help="Imprime o JSON completo do resumo no stdout.",
    )
    args = parser.parse_args()

    try:
        result = run_daily_summary(source=args.source, notify=not args.skip_notification)
    except Exception as error:
        print(f"Erro ao executar resumo diario: {error}", file=sys.stderr)
        return 1

    summary = result["summary"]
    counts = summary.get("counts", {})
    print(
        "Resumo diario sincronizado "
        f"para {summary.get('user_email', 'usuario-desconhecido')} "
        f"com {counts.get('assigned_items', 0)} itens e "
        f"{counts.get('blocked_items', 0)} bloqueios."
    )
    print(_build_identity_context_message(summary))
    if args.print_summary:
        print(json.dumps(summary, indent=2, ensure_ascii=True))
    if result["notification_result"]:
        print(result["notification_result"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())