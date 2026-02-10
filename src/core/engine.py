import psutil
import os
import time
import datetime
from typing import List, Dict, Any, Optional

class ProcessEngine:
    """
    Core logic for scanning, analyzing, and managing system processes.
    """

    @staticmethod
    def get_process_type(proc: psutil.Process) -> str:
        """Determines if process is User App or Service/Background."""
        try:
            # Fast Check: Typical Service Names
            name = proc.name().lower()
            system_procs = ['svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe', 'lsass.exe', 'smss.exe', 'system', 'registry', 'wininit.exe']
            if name in system_procs:
                return "Service"

            # Check for Session 0 (Services) on Windows
            if os.name == 'nt':
                try:
                    p_info = proc.as_dict(attrs=['pid', 'username'])
                    if p_info['pid'] == 0 or p_info['pid'] == 4:
                       return "Service"
                       
                    # We can't easily get session_id without specific attributes, 
                    # but typically apps have a username that is NOT NT AUTHORITY
                    user = p_info.get('username', '')
                    if user and 'nt authority' in user.lower():
                        return "Service"
                except:
                    pass

            return "App"
        except Exception:
            return "Service" # Default to Service if we can't determine (safest)

    @staticmethod
    def format_bytes(size: float) -> str:
        """Formats bytes into human-readable string."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.2f} {unit}"
            size /= 1024
        return f"{size:.2f} TB"

    @staticmethod
    def get_uptime(create_time: float) -> str:
        """Calculates process uptime string."""
        try:
            uptime_seconds = time.time() - create_time
            return str(datetime.timedelta(seconds=int(uptime_seconds)))
        except Exception:
            return "N/A"

    def scan_processes(self) -> List[Dict[str, Any]]:
        """
        Scans all running processes and returns a list of dictionaries with details.
        Optimized for performance.
        """
        results = []
        try:
            # Iterate using process_iter with needed attributes to minimize overhead
            attrs = ['pid', 'name', 'username', 'memory_info', 'create_time', 'cmdline', 'exe']
            for p in psutil.process_iter(attrs):
                try:
                    p_info = p.info # Use the cached info from process_iter
                    
                    # Store joined cmdline for easier searching
                    cmd_list = p_info.get('cmdline', [])
                    p_info['cmdline_str'] = " ".join(cmd_list) if cmd_list else ""
                    
                    # Determine type
                    # Note: We pass the process object itself for the type check methods if needed,
                    # but here we might need to rely on what we have.
                    # Let's improve get_process_type to use the info dict if possible or just use the PID/Name checks.
                    
                    # Re-implementing simplified type check to avoid re-querying process
                    p_type = "App"
                    name_lower = (p_info['name'] or "").lower()
                    user = (p_info['username'] or "")
                    
                    system_procs = ['svchost.exe', 'csrss.exe', 'winlogon.exe', 'services.exe', 'lsass.exe', 'smss.exe', 'system', 'registry', 'wininit.exe']
                    if name_lower in system_procs:
                        p_type = "Service"
                    elif 'nt authority' in user.lower():
                        p_type = "Service"
                    elif p_info['pid'] in (0, 4):
                        p_type = "Service"
                        
                    p_info['custom_type'] = p_type
                    p_info['memory_mb'] = p_info['memory_info'].rss / (1024 * 1024)
                    p_info['memory_str'] = self.format_bytes(p_info['memory_info'].rss)
                    p_info['uptime_str'] = self.get_uptime(p_info['create_time'])
                    
                    results.append(p_info)
                    
                except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
                    continue
        except Exception as e:
            print(f"Scan Error: {e}")

        # Sort: Services at bottom, High memory at top within apps
        results.sort(key=lambda x: (x['custom_type'] == "Service", -x['memory_mb']))
        return results

    def find_processes(self, query: str, processes: Optional[List[Dict[str, Any]]] = None) -> List[Dict[str, Any]]:
        """
        Filters processes based on a query. 
        If 'processes' list is provided, filters that list. Otherwise scans new.
        """
        if processes is None:
            processes = self.scan_processes()
            
        if not query:
            return processes

        query = query.lower()
        matching = []
        
        for p in processes:
            p_name = (p['name'] or "").lower()
            p_cmd = (p['cmdline_str'] or "").lower()
            p_pid = str(p['pid'])
            p_exe = (p['exe'] or "").lower()
            
            if (query in p_name or 
                query in p_cmd or 
                query in p_exe or
                p_pid.startswith(query)):
                matching.append(p)
                
        return matching

    def kill_process(self, pid: int) -> Dict[str, Any]:
        """
        Terminates a process by PID.
        Returns: {'success': bool, 'message': str}
        """
        try:
            proc = psutil.Process(pid)
            name = proc.name()
            proc.terminate()
            proc.wait(timeout=3)
            return {'success': True, 'message': f"Process '{name}' (PID: {pid}) terminated."}
        except psutil.NoSuchProcess:
            return {'success': False, 'message': f"Process (PID: {pid}) no longer exists."}
        except psutil.AccessDenied:
            return {'success': False, 'message': f"Access denied (PID: {pid}). Run as Admin."}
        except psutil.TimeoutExpired:
            try:
                proc.kill()
                return {'success': True, 'message': f"Process '{name}' (PID: {pid}) killed forcibly."}
            except Exception as e:
                 return {'success': False, 'message': f"Failed to force kill (PID: {pid}): {e}"}
        except Exception as e:
            return {'success': False, 'message': f"Error (PID: {pid}): {e}"}
