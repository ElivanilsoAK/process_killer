import psutil
import os
import time
import datetime
import sys
from typing import List, Optional, Any

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.text import Text
from rich import box

# Initialize Rich Console
console = Console()

class ProcessKillerApp:
    """
    A sophisticated CLI tool to manage and kill system processes.
    """

    def __init__(self):
        self.os_name = os.name

    def clear_screen(self) -> None:
        """Clears the terminal screen."""
        os.system('cls' if self.os_name == 'nt' else 'clear')

    def format_bytes(self, size: float) -> str:
        """Formats bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    def get_uptime(self, create_time: float) -> str:
        """Calculates process uptime."""
        try:
            uptime_seconds = time.time() - create_time
            return str(datetime.timedelta(seconds=int(uptime_seconds)))
        except Exception:
            return "N/A"

    def get_process_type(self, proc: psutil.Process) -> str:
        """Determines if process is User or Service/Background."""
        try:
            # maintain compatibility with different OS versions where session_id might not exist
            if hasattr(proc, 'info') and 'session_id' in proc.info:
                 if proc.info['session_id'] == 0:
                     return "[yellow]Service/Bg[/]"
            return "[green]User App[/]"
        except Exception:
            return "[dim]?[/]"

    def find_processes(self, query: str) -> List[psutil.Process]:
        """Searches for processes matching the query string."""
        matches = []
        
        with console.status(f"[bold cyan]Searching for '{query}'...", spinner="dots"):
            # Fetch attributes efficiently
            attrs = ['pid', 'name', 'exe', 'cmdline', 'memory_info', 'username', 'create_time']
            if self.os_name == 'nt':
                attrs.append('session_id')

            for proc in psutil.process_iter(attrs):
                try:
                    p_info = proc.info
                    p_name = p_info['name'] or ""
                    p_exe = p_info['exe'] or ""
                    p_cmd = " ".join(p_info['cmdline']) if p_info['cmdline'] else ""
                    
                    if (query.lower() in p_name.lower()) or \
                       (query.lower() in p_exe.lower()) or \
                       (query.lower() in p_cmd.lower()):
                        matches.append(proc)
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
                    
        return matches

    def kill_process(self, proc: psutil.Process) -> bool:
        """Terminates a process with safety checks."""
        pid = proc.pid
        name = "Unknown"
        try:
            name = proc.name()
            proc.terminate()
            proc.wait(timeout=3)
            console.print(f"[green]✔ Process '{name}' (PID: {pid}) terminated.[/]")
            return True
        except psutil.NoSuchProcess:
            console.print(f"[yellow]⚠ Process '{name}' (PID: {pid}) already gone.[/]")
        except psutil.AccessDenied:
            console.print(f"[bold red]✘ Access denied (PID: {pid}). Run as Admin.[/]")
        except psutil.TimeoutExpired:
            console.print(f"[yellow]⚠ Process '{name}' (PID: {pid}) hung. Forcing kill...[/]")
            try:
                proc.kill()
                console.print(f"[bold green]✔ Process '{name}' (PID: {pid}) killed forcibly.[/]")
                return True
            except Exception as e:
                 console.print(f"[bold red]✘ Failed to kill (PID: {pid}): {e}[/]")
        except Exception as e:
            console.print(f"[bold red]✘ Error (PID: {pid}): {e}[/]")
        return False

    def display_results(self, matches: List[psutil.Process]) -> List[int]:
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
        
        for p in matches:
            try:
                p_info = p.info
                pid = str(p_info['pid'])
                name = p_info['name']
                p_type = self.get_process_type(p)
                user = p_info.get('username') or "[red]Access Denied[/]"
                
                # Truncate user for better UI
                if "Access Denied" not in user and len(user) > 15:
                    user = user[:13] + "..."
                
                mem = self.format_bytes(p_info['memory_info'].rss)
                uptime = self.get_uptime(p_info['create_time'])
                
                exe = p_info['exe'] or ""
                # Smart truncate path from the left to show filename
                if len(exe) > 40:
                    exe = "..." + exe[-37:]
                
                table.add_row(pid, name, p_type, user, mem, uptime, exe)
                valid_pids.append(p_info['pid'])
            except (psutil.NoSuchProcess, psutil.AccessDenied):
                continue

        console.print(table)
        return valid_pids

    def run(self):
        """Main application loop."""
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

            matches = self.find_processes(query)
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
                    for p in matches:
                        self.kill_process(p)
                    Prompt.ask("\n[dim]Press Enter to continue...[/]")
            
            elif choice == "2":
                pid_str = Prompt.ask("[bold yellow]Enter PID[/]")
                if pid_str.isdigit() and int(pid_str) in valid_pids:
                    target = next((p for p in matches if p.pid == int(pid_str)), None)
                    if target:
                        self.kill_process(target)
                        Prompt.ask("\n[dim]Press Enter to continue...[/]")
                else:
                    console.print("[bold red]Invalid PID from the displayed list.[/]")
                    time.sleep(1.5)

if __name__ == "__main__":
    try:
        app = ProcessKillerApp()
        app.run()
    except KeyboardInterrupt:
        console.print("\n[bold red]Exiting...[/]")
