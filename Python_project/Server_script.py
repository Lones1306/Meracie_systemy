import socket
import threading
import time
import math

# Konfigurácia
HOST = '127.0.0.1'
PORT = 12345
#TODO: omega robi nieco inak, neni priamo naviazana na pocet amplitud za sekundu

# Globálne premené pre generovaný signál
generated_signal = []
received_data = []

server_running = True  # Globálna premenná pre ukončenie servera

def generate_signal(A, f):
    """Generuje sínusový signál s amplitúdou A a frekvenciou f"""
    global server_running
    omega = 2 * math.pi * f
    t = 0
    dt = 0.001  # Interval generovania (1000 Hz vzorkovacia frekvencia)

    while server_running:
        value = A * math.sin(omega * t)
        generated_signal.append(value)

        if len(generated_signal) > 2000:
            generated_signal.pop(0)

        t += dt
        time.sleep(dt)

def run_server(A, f):
    """Spustí UDP server a odpovedá na požiadavky klientov"""
    global server_running
    server_running = True  # Reset pri štarte servera

    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.bind((HOST, PORT))

        print(f"Server beží na {HOST}:{PORT} s A={A}, f={f}")

        # Spustenie vlákna na generovanie signálu
        signal_thread = threading.Thread(target=generate_signal, args=(A, f), daemon=True)
        signal_thread.start()

        while server_running:
            try:
                data, addr = sock.recvfrom(1024)
                decoded_data = data.decode()

                if decoded_data == "STOP":
                    print("Prijatý STOP signál. Server sa vypína...")
                    server_running = False
                    break  # Ukončí server

                if decoded_data == "request":
                    if generated_signal:
                        latest_value = generated_signal[-1]
                        response = f"{latest_value:.2f}"
                        sock.sendto(response.encode(), addr)
                    else:
                        sock.sendto(b"No signal data", addr)
                else:
                    try:
                        value = float(decoded_data)
                        received_data.append(value)
                        if len(received_data) > 2000:
                            received_data.pop(0)
                        print(f"Prijatá hodnota: {value:.2f} od {addr}")
                    except ValueError:
                        print(f"Neplatná hodnota: {decoded_data} od {addr}")

            except Exception as e:
                print(f"Chyba servera: {e}")

        print("Server bol bezpečne ukončený.")


