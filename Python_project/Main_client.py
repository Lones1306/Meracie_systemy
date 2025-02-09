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
from scipy.signal import butter, filtfilt

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

        # Prepojenie tlačidiel
        self.Start_button.clicked.connect(self.start_measurement)
        self.Stop_button.clicked.connect(self.stop_measurement)
        self.inputs_pushButton.clicked.connect(self.open_input_dialog)

        self.running = False
        self.server_thread = None
        self.client_thread = None

        #incialiazacia pociatocnych hodnot
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
        # otvori dialog a aktualizuje
        dialog = QDialog(self)
        ui = Ui_Dialog()
        ui.setupUi(dialog)

        # Nastavenie aktual hodnot v dialog
        ui.Amplituda_doubleSpinBox.setValue(self.amplitude)
        ui.Frekvencia_doubleSpinBox.setValue(self.omega)

        # Prepojenie tlacidiel
        ui.Apply_pushButton.clicked.connect(lambda: self.update_values(ui, dialog))
        ui.Close_pushButton.clicked.connect(dialog.close)

        if dialog.exec_():  # ok uloz
            self.update_values(ui, dialog)

    def update_values(self, ui, dialog):
        # aktualizuje hodnoty po ok v dialog
        self.amplitude = ui.Amplituda_doubleSpinBox.value()
        self.omega = ui.Frekvencia_doubleSpinBox.value()
        dialog.accept()  # close dialog

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
            time.sleep(2)  # spustenie servera

            # Spustenie klienta
            self.start_client()

    def stop_measurement(self):
        #stop measure and server
        self.running = False
        self.Stop_button.setEnabled(False)

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.sendto(b"STOP", (HOST, PORT))  # server stop


    def start_client(self):
        #klient v novom vlakne
        self.client_thread = threading.Thread(target=self.run_client, daemon=True)
        self.client_thread.start()

    def run_client(self):
        DAMPING_FACTOR = 0.98  # Tlmenie na redukciu driftovania
        HIGH_PASS_ALPHA = 0.96  # HP filter pre rýchlosť
        TRAPEZOIDAL = True  # Použijeme metódu trapézov
        POSITION_CORRECTION_GAIN = 0.008  # Miernejšia korekcia polohy
        POSITION_INTEGRAL_GAIN = 0.00005

        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            sock.settimeout(0.01)
            position = 0.0
            velocity = 0.0
            velocity_drift = 0.0
            position_drift = 0.0
            prev_acc = 0.0
            position_integral = 0.0
            last_time = time.time()

            acc_data = []
            vel_data = []
            pos_data = []
            force_data = []
            stress_data = []
            time_data = []
            start_time = time.time()

            while self.running:
                try:
                    sock.sendto(b"request", (HOST, PORT))
                    data, _ = sock.recvfrom(1024)
                    acc = float(data.decode())

                    # Časový krok
                    current_time = time.time()
                    dt = current_time - last_time
                    last_time = current_time

                    # Integrácia zrýchlenia na rýchlosť (trapezoidálna metóda)
                    if TRAPEZOIDAL:
                        velocity += 0.5 * (acc + prev_acc) * dt
                    else:
                        velocity += acc * dt  # Eulerova metóda

                    velocity *= DAMPING_FACTOR  # Tlmenie driftu

                    # Korekcia driftu rýchlosti (HP filter)
                    velocity_drift = HIGH_PASS_ALPHA * velocity_drift + (1 - HIGH_PASS_ALPHA) * velocity
                    velocity -= velocity_drift

                    # Integrácia rýchlosti na polohu (trapezoidálna metóda)
                    if TRAPEZOIDAL:
                        position += 0.5 * (velocity + velocity_drift) * dt
                    else:
                        position += velocity * dt

                    # Korekcia driftu polohy (slabý LP filter + P regulátor)
                    position_integral += position * dt
                    position -= POSITION_CORRECTION_GAIN * position + POSITION_INTEGRAL_GAIN * position_integral

                    prev_acc = acc


                    # Výpočet síl a napätí
                    force = (3 * self.E * self.I * position) / (self.L ** 3)
                    moment = force * self.L
                    sigma = (moment * self.y_max) / self.I
                    tau = 2 * (force / self.Area)
                    stress = (sigma ** 2 + 3 * tau ** 2) ** 0.5

                    # Ukladanie dát do listov
                    acc_data.append(acc)
                    vel_data.append(velocity)
                    pos_data.append(position)
                    force_data.append(force)
                    stress_data.append(stress)
                    time_data.append(current_time - start_time)

                    if len(acc_data) > 500:
                        acc_data.pop(0)
                        vel_data.pop(0)
                        pos_data.pop(0)
                        force_data.pop(0)
                        stress_data.pop(0)
                        time_data.pop(0)

                        # Graf napätia
                        if not hasattr(self, '_stress_line'):
                            # krivku napatia a horizontalnu red line na pre self.save
                            self._stress_line, = self.stress_graph.ax.plot([], [], label="Napätie (MPa)")
                            self._save_line = self.stress_graph.ax.axhline(self.save, color='r', linestyle='--',
                                                                           label='Maximalne dovolene napätie')
                            self.stress_graph.ax.set_xlabel("Čas [s]")
                            self.stress_graph.ax.set_ylabel("Napätie [MPa]")
                            self.stress_graph.ax.legend()

                        # Aktualizujeme dáta pre krivku napätia
                        self._stress_line.set_data(time_data, stress_data)
                        # Aktualizujeme horizontálnu čiaru (v prípade, že by sa self.save menilo)
                        self._save_line.set_ydata([self.save, self.save])

                        # Zmena pozadia grafu, ak napätie prekročí self.save
                        if stress > self.save:
                            self.stress_graph.ax.set_facecolor('red')
                        else:
                            self.stress_graph.ax.set_facecolor('white')

                        self.stress_graph.ax.relim()
                        self.stress_graph.ax.autoscale_view()
                        self.stress_graph.draw()

                        #Graf integrácie
                        if len(self.integration_graph.ax.lines) == 0:
                            self.integration_graph.ax.plot([], [], label="Zrýchlenie (mm/s²)")
                            self.integration_graph.ax.plot([], [], label="Rýchlosť (mm/s)")
                            self.integration_graph.ax.plot([], [], label="Poloha (mm)")
                            # Popis osí (bez Y) a legenda
                            self.integration_graph.ax.set_xlabel("Čas [s]")
                            # Nepíšeme set_ylabel -> ostane bez popisu
                            self.integration_graph.ax.legend()

                        self.integration_graph.ax.lines[0].set_data(time_data, acc_data)
                        self.integration_graph.ax.lines[1].set_data(time_data, vel_data)
                        self.integration_graph.ax.lines[2].set_data(time_data, pos_data)
                        self.integration_graph.ax.relim()
                        self.integration_graph.ax.autoscale_view()
                        self.integration_graph.draw()

                        # Graf sily
                        if len(self.force_graph.ax.lines) == 0:
                            self.force_graph.ax.plot([], [], label="Sila (N)", color='r')
                            # Popis osí a legenda
                            self.force_graph.ax.set_xlabel("Čas [s]")
                            self.force_graph.ax.set_ylabel("Sila [N]")
                            #self.force_graph.ax.legend()

                        self.force_graph.ax.lines[0].set_data(time_data, force_data)
                        self.force_graph.ax.relim()
                        self.force_graph.ax.autoscale_view()
                        self.force_graph.draw()

                except socket.timeout:
                    print("Časový limit prijímania vypršal")
                except Exception as e:
                    print(f"Chyba: {e}")

                time.sleep(0.001)  # Počkame na ďalší cyklus

    def update_graphs(self):
        """Aktualizuje grafy v GUI"""
        self.Integration.clear()
        self.Force.clear()
        self.stress.clear()

        # Vykreslenie grafov
        self.acc_plot.setData(self.time_data, self.acc_data)
        self.vel_plot.setData(self.time_data, self.vel_data)
        self.pos_plot.setData(self.time_data, self.pos_data)
        self.force_plot.setData(self.time_data, self.force_data)
        self.stress_plot.setData(self.time_data, self.stress_data)

    def update_list_widgets(self, acc, vel, pos, force, stress):
        """Aktualizuje QListWidget s novými hodnotami"""
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


