from scapy.all import sniff, IP, TCP, Raw
from datetime import datetime

def parse_modbus(packet):
    if packet.haslayer(TCP) and packet[TCP].dport == 502:
        try:
            raw_data = packet[Raw].load
            function_code = raw_data[7]  # Modbus FC at byte 8
            return {
                'src_ip': packet[IP].src,
                'dst_ip': packet[IP].dst,
                'timestamp': datetime.now(),
                'packet_len': len(packet),
                'function_code': function_code
            }
        except:
            return None

def capture_packets(callback):
    sniff(filter="tcp port 502", prn=lambda pkt: callback(parse_modbus(pkt)), store=0)
