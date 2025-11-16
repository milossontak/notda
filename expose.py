#!/usr/bin/env python3
"""
Skript pro automatické vystavení služby na internet pomocí ngrok.
Vyžaduje nainstalovaný ngrok: https://ngrok.com/download
"""

import subprocess
import sys
import time
import signal
import os
from pathlib import Path

def check_ngrok_installed():
    """Zkontroluje, zda je ngrok nainstalován."""
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_ngrok_auth():
    """Zkontroluje, zda je ngrok autentizovaný."""
    try:
        # Zkontrolovat konfigurační soubor ngrok
        ngrok_config_path = os.path.expanduser("~/.ngrok2/ngrok.yml")
        if os.path.exists(ngrok_config_path):
            with open(ngrok_config_path, 'r') as f:
                config = f.read()
                if 'authtoken' in config.lower():
                    return True
        
        # Pokud není konfigurační soubor, zkusíme spustit ngrok a zachytit chybu
        # Použijeme port, který pravděpodobně není obsazený
        test_port = 9999
        process = subprocess.Popen(
            ['ngrok', 'http', str(test_port)],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        time.sleep(1)  # Počkat na start
        process.terminate()
        process.wait(timeout=2)
        
        stdout, stderr = process.communicate()
        output = (stdout + stderr).lower()
        
        # Pokud obsahuje chybovou zprávu o autentizaci
        if 'authtoken' in output or 'authentication failed' in output or 'err_ngrok_4018' in output:
            return False
        return True
    except Exception:
        # Při jakékoli chybě předpokládáme, že není autentizovaný
        return False

def start_server():
    """Spustí FastAPI server."""
    print("Spouštím FastAPI server...")
    # Použijeme python3 pokud je dostupný, jinak sys.executable
    python_cmd = 'python3' if subprocess.run(['which', 'python3'], capture_output=True).returncode == 0 else sys.executable
    
    # Zkontrolujte, zda není port 8000 obsazený
    check_port = subprocess.run(['lsof', '-ti', ':8000'], capture_output=True)
    if check_port.returncode == 0:
        pid = check_port.stdout.decode().strip()
        print(f"⚠️  Varování: Port 8000 je obsazený procesem PID {pid}")
        print("Zkusím ho ukončit...")
        try:
            subprocess.run(['kill', pid], check=True)
            time.sleep(1)
        except subprocess.CalledProcessError:
            print("❌ Nepodařilo se ukončit proces. Použijte jiný port nebo ukončete proces ručně.")
            sys.exit(1)
    
    return subprocess.Popen(
        [python_cmd, 'app.py'],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT  # Sloučit stdout a stderr
    )

def start_ngrok(port=8000):
    """Spustí ngrok tunel."""
    print(f"Spouštím ngrok tunel na portu {port}...")
    # Spustit ngrok s unbuffered výstupem pro lepší zachycení chyb
    return subprocess.Popen(
        ['ngrok', 'http', str(port)],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        bufsize=1
    )

def main():
    if not check_ngrok_installed():
        print("❌ Chyba: Ngrok není nainstalován!")
        print("Stáhněte si ho z: https://ngrok.com/download")
        print("Nebo použijte jiný způsob vystavení služby (viz README.md)")
        sys.exit(1)
    
    # Zkontrolovat autentizaci ngrok
    print("Kontroluji autentizaci ngrok...")
    if not check_ngrok_auth():
        print("\n" + "="*60)
        print("⚠️  NGROK VYŽADUJE AUTENTIZACI")
        print("="*60)
        print("\nNgrok vyžaduje účet a authtoken pro použití.")
        print("\nPostup:")
        print("1. Vytvořte si účet na: https://dashboard.ngrok.com/signup")
        print("2. Získejte authtoken na: https://dashboard.ngrok.com/get-started/your-authtoken")
        print("3. Nastavte authtoken příkazem:")
        print("   ngrok config add-authtoken VÁŠ_AUTHTOKEN")
        print("\nAlternativně můžete použít Cloudflare Tunnel (zdarma, bez registrace):")
        print("   cloudflared tunnel --url http://localhost:8000")
        print("="*60 + "\n")
        sys.exit(1)
    
    # Zkontrolujte, zda existuje app.py
    if not Path('app.py').exists():
        print("Chyba: Soubor app.py nebyl nalezen!")
        sys.exit(1)
    
    server_process = None
    ngrok_process = None
    
    def cleanup(signum=None, frame=None):
        """Ukončí všechny procesy při ukončení."""
        print("\n\nUkončuji procesy...")
        if server_process:
            server_process.terminate()
        if ngrok_process:
            ngrok_process.terminate()
        print("Hotovo!")
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    try:
        # Spustit server
        server_process = start_server()
        time.sleep(2)  # Počkat, až se server spustí
        
        # Spustit ngrok
        ngrok_process = start_ngrok()
        time.sleep(3)  # Počkat, až se ngrok připojí
        
        print("\n" + "="*60)
        print("Služba je spuštěna!")
        print("="*60)
        print("\nLokální URL: http://localhost:8000")
        print("\nPro získání veřejné URL otevřete:")
        print("http://localhost:4040 (ngrok webové rozhraní)")
        print("\nNebo použijte ngrok API:")
        print("curl http://localhost:4040/api/tunnels")
        print("\nStiskněte Ctrl+C pro ukončení")
        print("="*60 + "\n")
        
        # Čekat na ukončení
        while True:
            time.sleep(1)
            if server_process.poll() is not None:
                print("\n❌ Server se neočekávaně ukončil!")
                # Zobrazit chybové zprávy ze serveru
                output = server_process.stdout.read().decode('utf-8', errors='ignore')
                if output:
                    print("Výstup ze serveru:")
                    print(output)
                break
            if ngrok_process.poll() is not None:
                print("\n❌ Ngrok se neočekávaně ukončil!")
                # Zobrazit výstup z ngrok
                try:
                    output = ngrok_process.stdout.read()
                    if output:
                        print("\nVýstup z ngrok:")
                        print(output)
                    
                    # Kontrola běžných chyb
                    output_str = str(output).lower()
                    if 'authtoken' in output_str or 'authentication' in output_str:
                        print("\n" + "="*60)
                        print("⚠️  NGROK VYŽADUJE AUTENTIZACI")
                        print("="*60)
                        print("\nNastavte authtoken příkazem:")
                        print("ngrok config add-authtoken VÁŠ_AUTHTOKEN")
                        print("\nZískejte authtoken na: https://dashboard.ngrok.com/get-started/your-authtoken")
                        print("="*60)
                except Exception as e:
                    print(f"Nepodařilo se načíst výstup z ngrok: {e}")
                break
    
    except Exception as e:
        print(f"Chyba: {e}")
        cleanup()

if __name__ == "__main__":
    main()

