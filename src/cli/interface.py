import os
import time
from typing import List, Dict, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich import box

from src.core.engine import ProcessEngine

# Initialize Rich Console
console = Console()

class CLIInterface:
    """
    Command Line Interface for Process Manager.
    """

    def __init__(self):
        self.engine = ProcessEngine()
        self.os_name = os.name

    def clear_screen(self) -> None:
        """Clears the terminal screen."""
        os.system('cls' if self.os_name == 'nt' else 'clear')

    def display_results(self, matches: List[Dict[str, Any]]) -> List[int]:
        """Displays the search results in a beautiful table."""
        if not matches:
            console.print(Panel(f"[bold red]No processes found matching your query.[/]", title="Search Results", border_style="red"))
            return []

        table = Table(title=f"Found [bold cyan]{len(matches)}[/] Process(es)", box=box.ROUNDED, header_style="bold white on blue")
        
        table.add_column("PID", style="cyan", justify="right")
        table.add_column("Name", style="white")
        table.add_column("Type", justify="center")
        table.add_column("User", style="magenta")
        table.add_column("Memory", justify="right", style="green")
        table.add_column("Uptime", justify="right")
        table.add_column("Path", style="dim", no_wrap=True)

        valid_pids = []
        
        for p_info in matches:
            pid = str(p_info['pid'])
            name = p_info['name']
            
            p_type = p_info.get('custom_type', 'App')
            if p_type == "Service":
                p_type = "[yellow]Service/Bg[/]"
            else:
                p_type = "[green]User App[/]"

            user = p_info.get('username') or "[red]Access Denied[/]"
            if "Access Denied" not in user and len(user) > 15:
                user = user[:13] + "..."
            
            mem = p_info.get('memory_str', 'N/A')
            uptime = p_info.get('uptime_str', 'N/A')
            
            exe = p_info.get('exe') or ""
            if len(exe) > 40:
                exe = "..." + exe[-37:]
            
            table.add_row(pid, name, p_type, user, mem, uptime, exe)
            valid_pids.append(p_info['pid'])

        console.print(table)
        return valid_pids

    def run(self):
        """Main CLI loop."""
        while True:
            self.clear_screen()
            console.print(Panel.fit(
                "[bold white]PROCESS MANAGER ELITE[/]\n[italic cyan]Advanced System Control Tool[/]", 
                border_style="cyan",
                padding=(1, 4)
            ))
            
            query = Prompt.ask("\n[bold yellow]Search[/] (Name/Path/ID) or [bold red]'exit'[/]").strip()
            
            if query.lower() in ['exit', 'quit', 'q']:
                console.print("[bold cyan]Goodbye![/]")
                break
            
            if not query:
                continue

            with console.status(f"[bold cyan]Searching for '{query}'...", spinner="dots"):
                matches = self.engine.find_processes(query)
            
            valid_pids = self.display_results(matches)

            if not valid_pids:
                Prompt.ask("\n[dim]Press Enter to continue...[/]")
                continue
            
            console.print("\n[bold]Options:[/]")
            console.print(" [bold cyan]1.[/] Kill [bold red]ALL[/] listed")
            console.print(" [bold cyan]2.[/] Kill [bold yellow]ONE[/] by PID")
            console.print(" [bold cyan]3.[/] Try New Search")
            
            choice = Prompt.ask("\n[bold]Select[/]", choices=["1", "2", "3"], default="3")

            if choice == "1":
                if Confirm.ask(f"[bold red]⚠ Are you SURE you want to kill {len(valid_pids)} processes?[/]", default=False):
                    for pid in valid_pids:
                        res = self.engine.kill_process(pid)
                        if res['success']:
                             console.print(f"[green]✔ {res['message']}[/]")
                        else:
                             console.print(f"[red]✘ {res['message']}[/]")
                    Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
            elif choice == "2":
                pid_str = Prompt.ask("[bold yellow]Enter PID[/]")
                if pid_str.isdigit() and int(pid_str) in valid_pids:
                    res = self.engine.kill_process(int(pid_str))
                    if res['success']:
                         console.print(f"[green]✔ {res['message']}[/]")
                    else:
                         console.print(f"[red]✘ {res['message']}[/]")
                    Prompt.ask("\n[dim]Press Enter to continue...[/]")
                else:
                    console.print("[bold red]Invalid PID from the displayed list.[/]")
                    time.sleep(1.5)
