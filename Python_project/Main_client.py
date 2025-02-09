import sys
import threading
import socket
import time
import numpy as np
from PyQt5 import QtWidgets, uic
from PyQt5.QtWidgets import QApplication, QMainWindow, QDialog
from Dialog_input import Ui_Dialog
from PyQt5.QtWidgets import QListWidgetItem
from PyQt5.QtWidgets import QWidget, QVBoxLayout
from Server_script import run_server
from PyQt5.QtWidgets import QWidget
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure

#   py -m PyQt5.uic.pyuic -x Main_window.ui -o Main_window.py
#   py -m PyQt5.uic.pyuic -x Dialog_input.ui -o Dialog_input.py

HOST = '127.0.0.1'
PORT = 12345
DT = 0.001


class MplCanvas(FigureCanvas, QWidget):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.figure = Figure(figsize=(width, height), dpi=dpi)
        self.ax = self.figure.add_subplot(111)  # Vytvorenie subplotu

        super().__init__(self.figure)  # Správne dedenie z FigureCanvasQTAgg
        self.setParent(parent)

        layout = parent.layout()  # Použitie existujúceho layoutu
        if layout:
            layout.addWidget(self)  # Pridaj priamo seba (MplCanvas)


class MainApp(QMainWindow):
    def __init__(self):
        super(MainApp, self).__init__()
        uic.loadUi("Main_window.ui", self)

        # buttny
        self.Start_button.clicked.connect(self.start_measurement)
        self.Stop_button.clicked.connect(self.stop_measurement)
        self.inputs_pushButton.clicked.connect(self.open_input_dialog)

        self.running = False
        self.server_thread = None
        self.client_thread = None

        #pociatocne hodnot
        self.Priemer.setValue(80)
        self.Dlzka.setValue(1000)
        self.Youngov_modul.setValue(210)
        self.Re_mat.setValue(600)
        self.Bezpecnost.setValue(1.5)
        self.amplitude = 10000.0
        self.omega = 1

        # Napojenie matplotlib grafov na QWidgety z Qt Designer
        self.stress_graph = MplCanvas(self.Graph_Stress)  # Nevolaj .canvas
        self.integration_graph = MplCanvas(self.Graph_Integration)
        self.force_graph = MplCanvas(self.Graph_Force)

        # Nastavenie grafov do QWidget placeholderov
        layout1 = QVBoxLayout(self.Graph_Stress)
        layout1.addWidget(self.stress_graph)

        layout2 = QVBoxLayout(self.Graph_Integration)
        layout2.addWidget(self.integration_graph)

        layout3 = QVBoxLayout(self.Graph_Force)
        layout3.addWidget(self.force_graph)

    def open_input_dialog(self):
        # otvori dialok a aktualizuje hodnoty
        dialog = QDialog(self)
        ui = Ui_Dialog()
        ui.setupUi(dialog)

        # setValue
        ui.Amplituda_doubleSpinBox.setValue(self.amplitude)
        ui.Frekvencia_doubleSpinBox.setValue(self.omega)

        # tlacidla Apply a Close
        ui.Apply_pushButton.clicked.connect(lambda: self.update_values(ui, dialog))
        ui.Close_pushButton.clicked.connect(dialog.close)

        if dialog.exec_():  # Ak ok uloz
            self.update_values(ui, dialog)

    def update_values(self, ui, dialog):
        # aktualizacia po OK
        self.amplitude = ui.Amplituda_doubleSpinBox.value()
        self.omega = ui.Frekvencia_doubleSpinBox.value()
        dialog.accept()  # Zavrie dialóg

    def start_measurement(self):
        self.Stop_button.setEnabled(True)

        # mechanicke vlastnosti
        self.Re = self.Re_mat.value()
        self.E = self.Youngov_modul.value()
        self.L = self.Dlzka.value()
        self.D = self.Priemer.value()
        self.d = self.D * 0.8
        self.I = ((3.1415 * self.D ** 4) / 64) - ((3.1415 * self.d ** 4) / 64)
        self.y_max = self.D / 2
        self.k = self.Bezpecnost.value()
        self.save = self.Re/self.k
        self.Jp = (3.1415/32)*((self.D**4)-(self.d**4))
        self.Area = 3.1415*((self.D**2-self.d**2)/4)

        if not self.running:
            self.running = True

            A = self.amplitude
            f = self.omega

            # Spustenie servera v novom vlákne
            self.server_thread = threading.Thread(target=run_server, args=(A, f), daemon=True)
            self.server_thread.start()
            time.sleep(2)  # Počkame na spustenie servera

            # Spustenie klienta
            self.start_client()

    def stop_measurement(self):
        #Zastaví meranie a vypne server
        self.running = False
        self.Stop_button.setEnabled(False)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b"STOP", (HOST, PORT))  # server stop


    def start_client(self):
        #klient v novom vlakne
        self.client_thread = threading.Thread(target=self.run_client, daemon=True)
        self.client_thread.start()

    def run_client(self):
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(1)  # Timeout na prijímanie údajov
            position = 0.0
            velocity = 0.0
            time_offset = 0.0  # Posun časovej osi pre kontinuálne dáta

            # Inicializácia dátových polí pre historické hodnoty
            self.time_data = []
            self.acc_data = []
            self.vel_data = []
            self.pos_data = []
            self.force_data = []
            self.stress_data = []

            while self.running:
                try:
                    # Pošleme požiadavku na novú periódu dát
                    sock.sendto(b"request", (HOST, PORT))
                    data, _ = sock.recvfrom(65536)  # Zvýšený buffer pre celú periódu

                    # Konverzia prijatých dát na zoznam čísel
                    data_str = data.decode().strip()
                    acc_values = [float(val) for val in data_str.split()]

                    dt = DT  # Konštantný krok z definície

                    # **Odstránenie DC biasu zo zrýchlenia**
                    acc_mean = sum(acc_values) / len(acc_values)
                    acc_values = [a - acc_mean for a in acc_values]

                    velocity_values = [velocity]  # Začneme s poslednou hodnotou
                    position_values = [position]

                    # **Dvojitá integrácia zrýchlenia**
                    for acc in acc_values:
                        new_velocity = velocity_values[-1] + acc * dt
                        velocity_values.append(new_velocity)

                        new_position = position_values[-1] + new_velocity * dt
                        position_values.append(new_position)

                    # **Odstránenie DC biasu z rýchlosti**
                    vel_mean = sum(velocity_values) / len(velocity_values)
                    velocity_values = [v - vel_mean for v in velocity_values]

                    # **Reintegrácia polohy so skorigovanou rýchlosťou**
                    position_values = [position]
                    for v in velocity_values:
                        new_position = position_values[-1] + v * dt
                        position_values.append(new_position)

                    # Odstránenie prvého bodu (začiatok bol predchádzajúca hodnota)
                    velocity_values.pop(0)
                    position_values.pop(0)

                    # Aktualizácia posledných hodnôt pre ďalšiu iteráciu
                    velocity = velocity_values[-1]
                    position = position_values[-1]

                    # Výpočty síl a napätí
                    force_values = [(3 * self.E * self.I * pos) / (self.L ** 3) for pos in position_values]
                    moment_values = [force * self.L for force in force_values]
                    sigma_values = [(moment * self.y_max) / self.I for moment in moment_values]
                    tau_values = [2 * (force / self.Area) for force in force_values]
                    stress_values = [(sigma ** 2 + 3 * tau ** 2) ** 0.5 for sigma, tau in zip(sigma_values, tau_values)]

                    # Generovanie časovej osi pre periódu s kontinuálnym posunom
                    time_values = [time_offset + i * dt for i in range(len(acc_values))]
                    time_offset = time_values[-1] + dt  # Posun na ďalší segment

                    # Pridanie dát do historických zoznamov
                    self.time_data.extend(time_values)
                    self.acc_data.extend(acc_values)
                    self.vel_data.extend(velocity_values)
                    self.pos_data.extend(position_values)
                    self.force_data.extend(force_values)
                    self.stress_data.extend(stress_values)

                    # Orezanie starých dát, aby sa zabránilo preťaženiu grafu
                    MAX_POINTS = 5000
                    if len(self.time_data) > MAX_POINTS:
                        self.time_data = self.time_data[-MAX_POINTS:]
                        self.acc_data = self.acc_data[-MAX_POINTS:]
                        self.vel_data = self.vel_data[-MAX_POINTS:]
                        self.pos_data = self.pos_data[-MAX_POINTS:]
                        self.force_data = self.force_data[-MAX_POINTS:]
                        self.stress_data = self.stress_data[-MAX_POINTS:]

                    # Aktualizácia grafov
                    self.update_graphs(
                        self.time_data, self.acc_data, self.vel_data,
                        self.pos_data, self.force_data, self.stress_data
                    )

                except ValueError as e:
                    print(f"Chyba pri konverzii na čísla: {e}")
                except socket.timeout:
                    print("Časový limit prijímania vypršal")
                except Exception as e:
                    print(f"Chyba: {e}")

    def update_graphs(self, time_values, acc_values, velocity_values, position_values, force_values, stress_values):
        # Aktualizuje grafy v GUI po každej perióde

        # Graf napätia
        self.stress_graph.ax.clear()
        self.stress_graph.ax.plot(time_values, stress_values, label="Napätie (MPa)")
        self.stress_graph.ax.axhline(self.save, color='r', linestyle='--', label='Maximalne dovolene napätie')
        self.stress_graph.ax.set_xlabel("Čas [s]")
        self.stress_graph.ax.set_ylabel("Napätie [MPa]")
        self.stress_graph.ax.legend()
        self.stress_graph.draw()

        #Graf integrácie
        self.integration_graph.ax.clear()
        self.integration_graph.ax.plot(time_values, acc_values, label="Zrýchlenie (mm/s²)")
        self.integration_graph.ax.plot(time_values, velocity_values, label="Rýchlosť (mm/s)")
        self.integration_graph.ax.plot(time_values, position_values, label="Poloha (mm)")
        self.integration_graph.ax.set_xlabel("Čas [s]")
        self.integration_graph.ax.legend()
        self.integration_graph.draw()

        #Graf sily
        self.force_graph.ax.clear()
        self.force_graph.ax.plot(time_values, force_values, label="Sila (N)", color='r')
        self.force_graph.ax.set_xlabel("Čas [s]")
        self.force_graph.ax.set_ylabel("Sila [N]")
        #self.force_graph.ax.legend()
        self.force_graph.draw()

    def update_list_widgets(self, acc, vel, pos, force, stress):
        #Aktualizuje QListWidget s novými hodnotami
        self.Integration.addItem(QListWidgetItem(f"Acc: {acc:.2f}, Vel: {vel:.2f}, Pos: {pos:.5f}"))
        self.Force.addItem(QListWidgetItem(f"Force: {force:.2f} N"))
        self.stress.addItem(QListWidgetItem(f"Stress: {stress:.2f} Pa"))

        # Udržiavanie maximálneho počtu položiek
        if self.Integration.count() > 100:
            self.Integration.takeItem(0)
        if self.Force.count() > 100:
            self.Force.takeItem(0)
        if self.stress.count() > 100:
            self.stress.takeItem(0)



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainApp()
    window.show()
    sys.exit(app.exec_())


