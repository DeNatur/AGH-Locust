# AGH-Locust WORK IN PROGRESS

Repository for storing scripts

# Wymagania

CUDA 10.0 i cudnn
# Instrukcja:
1. Pobrać repozytorium i wypakować
2. Pobrać oba pliki yolo weights i wkleić do folderu bin: https://drive.google.com/drive/folders/1SkTj4s6jwr7jPef7NJRQqRGQGJ2dW4m4?usp=sharing
3. Uruchomić AIdrone(pamiętać o podłączeniu kamery inaczej będzie wyrzucać błąd)
4. Podłączyć arduino, wpisać baud rate i odpowiedni port i kliknąć connect

W lini 157 w AIdrone.py można edytować co się wysyła do arduino: self.arduino_serial.write("Tu wpisuje się co chce się wysłać")


