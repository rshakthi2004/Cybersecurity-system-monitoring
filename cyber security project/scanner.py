#Network scanning 
import socket

def scan_ports(host="127.0.0.1"):
    
    open_ports = []

    print(f"Scanning ports on {host}...")

    for port in range(20, 200):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(0.1)
        try:
            if s.connect_ex((host, port)) == 0:
                open_ports.append(port)
                print(f"Port {port} is OPEN")
        except Exception as e:
            print(f"Error scanning port {port}: {e}")
        finally:
            s.close()

    print("\nScan complete!")
    print(f"Open ports on {host}: {open_ports}")
    return open_ports


if __name__ == "__main__":
   
    scan_ports("127.0.0.1")