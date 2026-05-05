import httpx
import asyncio
import hashlib
import ssl
import socket
import urllib.parse
import re
import whois
from datetime import datetime
from bs4 import BeautifulSoup
from playwright.async_api import async_playwright

# --- 1. MODUL PERTAHANAN DASAR ---
async def detect_cloudflare(url: str):
    """Modul Baru: Mendeteksi apakah website menggunakan proteksi Cloudflare."""
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(url)
            # Cloudflare biasanya menyertakan header 'Server: cloudflare' 
            # atau header 'cf-ray' / 'cf-cache-status'
            headers = res.headers
            is_cf = any(key.lower() in ["server", "cf-ray", "cf-cache-status"] 
                        and "cloudflare" in str(headers.get(key)).lower() 
                        for key in headers)
            return {"is_cloudflare": is_cf}
    except:
        return {"is_cloudflare": False}

async def scan_security_headers(url: str):
    headers_to_check = ["Strict-Transport-Security", "Content-Security-Policy", "X-Frame-Options", "X-Content-Type-Options"]
    results = {"headers_missing": []}
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(url)
            results["headers_missing"] = [h for h in headers_to_check if h not in res.headers]
    except: pass
    return results

async def check_defacement(url: str):
    results = {"content_hash": None}
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(url)
            body = BeautifulSoup(res.text, 'html.parser').find('body')
            if body: results["content_hash"] = hashlib.sha256(body.get_text(strip=True).encode('utf-8')).hexdigest()
    except: pass
    return results

def check_ssl_expiry(url: str):
    try:
        hostname = url.replace("https://", "").replace("http://", "").split('/')[0]
        context = ssl.create_default_context()
        with socket.create_connection((hostname, 443), timeout=5) as sock:
            with context.wrap_socket(sock, server_hostname=hostname) as ssock:
                cert = ssock.getpeercert()
                exp = datetime.strptime(cert['notAfter'], '%b %d %H:%M:%S %Y %Z')
                return {"days_left": (exp - datetime.now()).days}
    except: return {"days_left": -1}

async def check_broken_links(url: str):
    broken = []
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(url)
            links = BeautifulSoup(res.text, 'html.parser').find_all('a', href=True)[:10]
            for link in links:
                full_url = urllib.parse.urljoin(url, link['href'])
                if full_url.startswith('http'):
                    try:
                        if (await client.head(full_url, follow_redirects=True, timeout=5.0)).status_code >= 400:
                            broken.append(full_url)
                    except: broken.append(full_url)
    except: pass
    return {"broken_links": broken}

async def capture_screenshot(url: str, filepath: str):
    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True, channel="msedge") # Gunakan chrome/msedge lokal
            page = await browser.new_page()
            await page.goto(url, timeout=20000)
            await page.screenshot(path=filepath, full_page=True)
            await browser.close()
            return True
    except: return False

# --- 2. MODUL INTELIJEN LANJUTAN (BARU) ---
async def scan_open_ports(url: str):
    hostname = url.replace("https://", "").replace("http://", "").split('/')[0]
    ports_to_check = [21, 22, 3306]
    open_ports = []
    for port in ports_to_check:
        try:
            # Menggunakan timeout singkat untuk mendeteksi blocking
            reader, writer = await asyncio.wait_for(asyncio.open_connection(hostname, port), timeout=2.0)
            open_ports.append(port)
            writer.close()
            await writer.wait_closed()
        except Exception:
            # Jika koneksi ditolak atau gagal, kita anggap port tertutup/terproteksi
            continue
    return {"open_ports": open_ports}

async def fuzz_directories(url: str):
    """Mencari panel admin atau file backup yang disembunyikan."""
    paths = [".env", ".git/config", "phpmyadmin/", "wp-admin/", "backup.zip", "config.php.bak"]
    found = []
    base_url = url.rstrip('/')
    async with httpx.AsyncClient(timeout=5.0, verify=False) as client:
        for path in paths:
            try:
                res = await client.get(f"{base_url}/{path}")
                if res.status_code in [200, 401, 403] and "404" not in res.text:
                    found.append(path)
            except: continue
    return {"exposed_paths": found}

async def detect_api_keys(url: str):
    """Mencari kebocoran API Key di source code HTML."""
    leaked_keys = []
    patterns = {
        "Google API": r"AIza[0-9A-Za-z-_]{35}",
        "AWS Key": r"AKIA[0-9A-Z]{16}"
    }
    try:
        async with httpx.AsyncClient(timeout=10.0, verify=False) as client:
            res = await client.get(url)
            for key_name, pattern in patterns.items():
                if re.search(pattern, res.text):
                    leaked_keys.append(key_name)
    except: pass
    return {"leaked_keys": leaked_keys}

def check_whois(url: str):
    """Memeriksa masa kedaluwarsa domain."""
    try:
        domain = url.replace("https://", "").replace("http://", "").split('/')[0]
        domain_info = whois.whois(domain)
        exp_date = domain_info.expiration_date
        if type(exp_date) is list: exp_date = exp_date[0]
        if exp_date:
            return {"domain_days_left": (exp_date - datetime.now()).days}
    except: pass
    return {"domain_days_left": -1}

async def get_server_ip(url: str):
    try:
        hostname = url.replace("https://", "").replace("http://", "").split('/')[0]
        loop = asyncio.get_event_loop()
        # Beri timeout agar tidak menunggu terlalu lama jika DNS lambat
        ip = await asyncio.wait_for(loop.run_in_executor(None, socket.gethostbyname, hostname), timeout=5.0)
        return {"ip_address": ip, "protected": False}
    except (socket.gaierror, asyncio.TimeoutError):
        # Jika DNS gagal, berarti ada proteksi firewall atau DNS internal
        return {"ip_address": "Protected/Firewall", "protected": True}

# --- 3. ORKESTRATOR ---
async def run_full_scan(url: str):
    print(f"\n=== Memulai Patroli DevSecOps untuk {url} ===")
    
    t_headers = scan_security_headers(url)
    t_defacement = check_defacement(url)
    t_links = check_broken_links(url)
    t_ports = scan_open_ports(url)
    t_fuzz = fuzz_directories(url)
    t_api = detect_api_keys(url)
    t_ip = get_server_ip(url) # Menjalankan pencarian IP
    t_cf = detect_cloudflare(url)
    
    loop = asyncio.get_event_loop()
    t_ssl = loop.run_in_executor(None, check_ssl_expiry, url)
    t_whois = loop.run_in_executor(None, check_whois, url)
    
    # Menunggu semua proses termasuk pencarian IP
    res = await asyncio.gather(t_headers, t_defacement, t_links, t_ports, t_fuzz, t_api, t_ssl, t_whois, t_ip, t_cf)
    
    return {
        "headers": res[0], "defacement": res[1], "links": res[2], 
        "ports": res[3], "fuzz": res[4], "api": res[5], 
        "ssl": res[6], "whois": res[7], "ip_info": res[8], "cf_info": res[9] # Menyimpan hasil IP
    }