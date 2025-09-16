from scapy.all import sniff, IP, TCP, ICMP
import time
from collections import defaultdict


# Trackers for floods/scans
icmp_tracker = defaultdict(list)
tcp_tracker = defaultdict(list)

# Detection thresholds
ICMP_THRESHOLD = 5    # pings in 5 seconds = flood
SYN_THRESHOLD = 10    # SYNs in 5 seconds = scan

def detect(packet):
    if packet.haslayer(IP):
        src = packet[IP].src
        dst = packet[IP].dst

        # --- Detect ICMP pings / floods ---
        if packet.haslayer(ICMP):
            if packet[ICMP].type in [8, 0]:  # Echo request/reply
                print(f"[ICMP] Ping {src} -> {dst}")
                now = time.time()
                icmp_tracker[src].append(now)
                # Keep only last 5 seconds
                icmp_tracker[src] = [t for t in icmp_tracker[src] if now - t < 5]
                if len(icmp_tracker[src]) >= ICMP_THRESHOLD:
                    print(f"[ALERT] ICMP flood from {src}")

        # --- Detect TCP SYNs / scans ---
        if packet.haslayer(TCP):
            flags = packet[TCP].flags
            dport = packet[TCP].dport
            # SYN flag
            if flags & 0x02:
                print(f"[TCP] SYN {src} -> {dst}:{dport}")
                now = time.time()
                tcp_tracker[src].append(now)
                tcp_tracker[src] = [t for t in tcp_tracker[src] if now - t < 5]
                if len(tcp_tracker[src]) >= SYN_THRESHOLD:
                    print(f"[ALERT] Port scan detected from {src}")
            # NULL scan (no flags)
            elif flags == 0:
                print(f"[ALERT] NULL scan {src} -> {dst}:{dport}")
            # FIN scan
            elif flags & 0x01:
                print(f"[ALERT] FIN scan {src} -> {dst}:{dport}")

def start_sniffer():
    print("Starting lightweight NIDS... Press Ctrl+C to stop.")
    sniff(prn=detect, store=False)

if __name__ == "__main__":
    start_sniffer()
