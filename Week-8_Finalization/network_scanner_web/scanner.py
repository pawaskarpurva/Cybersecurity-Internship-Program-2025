# scanner.py
import ipaddress
import socket
from concurrent.futures import ThreadPoolExecutor, as_completed

def parse_ports(ports_text):
    """Parse ports string like '22 80 443' or '1-1024' or '22,80,443'."""
    if not ports_text:
        return []
    text = ports_text.replace(",", " ").strip()
    parts = text.split()
    ports = set()
    for p in parts:
        if "-" in p:
            try:
                a,b = p.split("-",1)
                a,b = int(a), int(b)
                if a> b: a,b = b,a
                ports.update(range(max(1,a), min(65535,b)+1))
            except:
                continue
        else:
            try:
                ports.add(int(p))
            except:
                continue
    return sorted([p for p in ports if 1 <= p <= 65535])
def grab_banner(ip, port, timeout=1.0):
    """Attempt to grab a banner from ip:port. Returns string (may be empty)."""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        s.connect((ip, port))
        # For HTTP-like ports, send a GET to elicit a response
        if port in (80, 8080, 8000):
            try:
                s.sendall(b"GET / HTTP/1.1\r\nHost: %b\r\n\r\n" % ip.encode())
            except:
                pass
        try:
            data = s.recv(2048)
            s.close()
            return data.decode(errors="ignore").strip()
        except:
            s.close()
            return ""
    except Exception:
        return ""  

def scan_port(ip, port, timeout=1.0):
    """Return (port, banner) if open, else None"""
    try:
        s = socket.socket()
        s.settimeout(timeout)
        res = s.connect_ex((ip, port))
        if res == 0:
            banner = grab_banner(ip, port, timeout=timeout)
            return (port, banner or "No banner")
        return None
    except Exception:
        return None

def scan_host(ip, ports, timeout=1.0, per_host_workers=40):
    """Scan one host concurrently across ports. Returns list of (ip,port,banner)."""
    if not ports:
        return []
    results = []
    with ThreadPoolExecutor(max_workers=min(per_host_workers, max(1, len(ports)))) as ex:
        futures = {ex.submit(scan_port, ip, p, timeout): p for p in ports}
        for f in as_completed(futures):
            r = f.result()
            if r:
                results.append((ip, r[0], r[1]))
    return results

def scan_subnet(subnet, ports_text, timeout=1.0, workers=200, per_host_workers=40, max_hosts=None):
    """
    Scan a subnet for given ports.
    Returns list of dicts: {"ip": ip, "port": port, "banner": banner}
    """
    ports = parse_ports(ports_text)
    net = ipaddress.ip_network(subnet, strict=False)
    all_hosts = list(str(ip) for ip in net.hosts())
    if max_hosts:
        try:
            all_hosts = all_hosts[:int(max_hosts)]
        except:
            pass

    results = []
    if not all_hosts:
        return results

    # parallelize across hosts
    with ThreadPoolExecutor(max_workers=min(workers, max(1, len(all_hosts)))) as ex:
        futures = {ex.submit(scan_host, ip, ports, timeout, per_host_workers): ip for ip in all_hosts}
        for f in as_completed(futures):
            host_results = f.result()
            for ip, port, banner in host_results:
                results.append({"ip": ip, "port": port, "banner": banner})
    results.sort(key=lambda r: (r["ip"], r["port"]))
    return results
