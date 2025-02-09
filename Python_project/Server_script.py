import socket
import threading
import time
import math
import numpy as np

# Konfigurácia
HOST = '127.0.0.1'
PORT = 12345
dt = 0.001  # Časový krok

def run_server(A, f):
    """Spustí UDP server a posiela periódy signálu v reálnom čase."""
    if f <= 0:
        print("Chyba: Frekvencia musí byť väčšia ako 0!")
        return

    omega = 2 * math.pi * f
    T = 1 / f  # Perióda signálu
    num_samples = int(T / dt)  # Počet vzoriek na periódu

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
                    start_time = time.time()
                    t_values = np.linspace(0, T, num_samples, endpoint=False)  # Rovnomerné časové vzorky
                    acc_values = A * np.sin(omega * t_values)

                    # Posielame dáta v tvare "čas akcelerácia" pre každú vzorku
                    data_str = "\n".join(f"{t:.6f} {a:.6f}" for t, a in zip(t_values, acc_values))
                    sock.sendto(data_str.encode(), addr)

                    # Počkám na ďalšiu periódu
                    elapsed_time = time.time() - start_time
                    time.sleep(max(0, T - elapsed_time))

            except Exception as e:
                print(f"Chyba servera: {e}")

        print("Server bol bezpečne ukončený.")

if __name__ == "__main__":
    A, f = 1.0, 1.0  # Tu môže byť zmenené podľa potreby
    server_thread = threading.Thread(target=run_server, args=(A, f), daemon=True)
    server_thread.start()
