"""
KwikLedgers - MCP Server: Windows Calendar & Notifications
Expoe ferramentas para enviar notificacoes Windows e gerenciar o calendario do Outlook.
Requer Windows com Outlook instalado.
"""
import os
import asyncio
from datetime import datetime, timedelta

from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent


server = Server("kwikledgers-windows")


@server.list_tools()
async def list_tools() -> list[Tool]:
    return [
        Tool(
            name="send_notification",
            description="Envia uma notificacao toast no Windows",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "message": {"type": "string"},
                    "urgency": {"type": "string", "enum": ["normal", "high"], "default": "normal"}
                },
                "required": ["title", "message"]
            }
        ),
        Tool(
            name="create_calendar_event",
            description="Cria um evento no calendario do Outlook",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "start": {"type": "string", "description": "ISO 8601: 2025-01-15T14:00:00"},
                    "end": {"type": "string", "description": "ISO 8601: 2025-01-15T15:00:00"},
                    "description": {"type": "string"},
                    "reminder_minutes": {"type": "integer", "default": 30}
                },
                "required": ["title", "start", "end"]
            }
        ),
        Tool(
            name="get_upcoming_deadlines",
            description="Retorna eventos dos proximos N dias do calendario do Outlook",
            inputSchema={
                "type": "object",
                "properties": {
                    "days": {"type": "integer", "default": 7}
                }
            }
        ),
        Tool(
            name="schedule_reminder",
            description="Agenda um lembrete recorrente baseado em titulo e data/hora",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {"type": "string"},
                    "remind_at": {"type": "string", "description": "ISO 8601"},
                    "message": {"type": "string"}
                },
                "required": ["title", "remind_at", "message"]
            }
        ),
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    try:
        result = await _dispatch(name, arguments)
        return [TextContent(type="text", text=result)]
    except Exception as e:
        return [TextContent(type="text", text=f"Erro: {str(e)}")]


async def _dispatch(name: str, arguments: dict) -> str:
    if name == "send_notification":
        return _send_notification(
            arguments["title"],
            arguments["message"],
            arguments.get("urgency", "normal")
        )
    if name == "create_calendar_event":
        return _create_calendar_event(
            arguments["title"],
            arguments["start"],
            arguments["end"],
            arguments.get("description", ""),
            arguments.get("reminder_minutes", 30)
        )
    if name == "get_upcoming_deadlines":
        return _get_upcoming_deadlines(arguments.get("days", 7))
    if name == "schedule_reminder":
        return _schedule_reminder(
            arguments["title"],
            arguments["remind_at"],
            arguments["message"]
        )
    return f"Ferramenta desconhecida: {name}"


# --- Implementacoes ---

def _send_notification(title: str, message: str, urgency: str = "normal") -> str:
    """Envia notificacao toast usando winotify."""
    try:
        from winotify import Notification, audio

        toast = Notification(
            app_id="KwikLedgers Dev Agent",
            title=title,
            msg=message,
            duration="short" if urgency == "normal" else "long"
        )
        if urgency == "high":
            toast.set_audio(audio.Default, loop=False)
        toast.show()
        return f"Notificacao enviada: {title}"
    except ImportError:
        # Fallback usando PowerShell se winotify nao estiver instalado
        import subprocess
        ps_script = f"""
        Add-Type -AssemblyName System.Windows.Forms
        $notify = New-Object System.Windows.Forms.NotifyIcon
        $notify.Icon = [System.Drawing.SystemIcons]::Information
        $notify.Visible = $true
        $notify.ShowBalloonTip(5000, '{title}', '{message}', [System.Windows.Forms.ToolTipIcon]::Info)
        """
        subprocess.run(["powershell", "-Command", ps_script], capture_output=True)
        return f"Notificacao enviada via PowerShell: {title}"


def _create_calendar_event(
    title: str, start: str, end: str,
    description: str = "", reminder_minutes: int = 30
) -> str:
    """Cria evento no Outlook via win32com."""
    import win32com.client
    from datetime import datetime

    outlook = win32com.client.Dispatch("Outlook.Application")
    appt = outlook.CreateItem(1)  # olAppointmentItem = 1

    appt.Subject = title
    appt.Body = description
    appt.Start = start
    appt.End = end
    appt.ReminderMinutesBeforeStart = reminder_minutes
    appt.ReminderSet = True
    appt.Save()

    return f"Evento criado no calendario: '{title}' em {start}"


def _get_upcoming_deadlines(days: int = 7) -> str:
    """Lê eventos do Outlook dos proximos N dias."""
    try:
        import win32com.client
        from datetime import datetime, timedelta

        outlook = win32com.client.Dispatch("Outlook.Application")
        namespace = outlook.GetNamespace("MAPI")
        calendar = namespace.GetDefaultFolder(9)  # olFolderCalendar = 9
        items = calendar.Items

        items.Sort("[Start]")
        items.IncludeRecurrences = True

        start = datetime.now()
        end = start + timedelta(days=days)

        restriction = (
            f"[Start] >= '{start.strftime('%m/%d/%Y %H:%M')}' "
            f"AND [Start] <= '{end.strftime('%m/%d/%Y %H:%M')}'"
        )
        restricted = items.Restrict(restriction)

        if restricted.Count == 0:
            return f"Nenhum evento nos proximos {days} dias."

        lines = [f"Proximos {days} dias:\n"]
        for item in restricted:
            lines.append(
                f"  {item.Start.strftime('%d/%m %H:%M')} — {item.Subject}"
            )
        return "\n".join(lines)

    except Exception as e:
        return f"Nao foi possivel ler o calendario: {e}"


def _schedule_reminder(title: str, remind_at: str, message: str) -> str:
    """Cria um evento curto no Outlook como lembrete."""
    start_dt = datetime.fromisoformat(remind_at)
    end_dt = start_dt + timedelta(minutes=15)
    return _create_calendar_event(
        title=f"[LEMBRETE] {title}",
        start=start_dt.isoformat(),
        end=end_dt.isoformat(),
        description=message,
        reminder_minutes=0
    )


# --- Entry point ---

async def main():
    async with stdio_server() as (read_stream, write_stream):
        await server.run(read_stream, write_stream, server.create_initialization_options())


if __name__ == "__main__":
    asyncio.run(main())
