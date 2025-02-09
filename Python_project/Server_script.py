import socket
import threading
import time
import math
import numpy as np

# Konfigurácia
HOST = '127.0.0.1'
PORT = 12345


def generate_signal(A, f, dt=0.001):
    """Generuje a vráti jednu periódu sínusového signálu."""
    omega = 2 * math.pi * f
    T = 1 / f  # Perióda signálu
    t_values = np.arange(0, T, dt)
    signal_values = A * np.sin(omega * t_values)
    return signal_values.tolist()


def run_server(A, f):
    """Spustí UDP server a odpovedá na požiadavky klientov."""
    signal_data = generate_signal(A, f)

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))

        print(f"Server beží na {HOST}:{PORT} s A={A}, f={f}")

        while True:
            try:
                data, addr = sock.recvfrom(1024)
                decoded_data = data.decode()

                if decoded_data == "STOP":
                    print("Prijatý STOP signál. Server sa vypína...")
                    break

                if decoded_data == "request":
                    response = ' '.join(map(str, signal_data))
                    sock.sendto(response.encode(), addr)

            except Exception as e:
                print(f"Chyba servera: {e}")

        print("Server bol bezpečne ukončený.")


if __name__ == "__main__":
    A, f = 1.0, 1.0  # Tu môže byť zmenené podľa potreby
    server_thread = threading.Thread(target=run_server, args=(A, f), daemon=True)
    server_thread.start()
