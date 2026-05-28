from flask import Flask, render_template, request
from datetime import datetime
from flask_socketio import SocketIO
from threading import Lock
from module import *
from datetime import datetime
import webbrowser
import logging
import time

logger = logging.getLogger("Flask-App")

enable_debug_logs: bool = False

match enable_debug_logs:
    case True:
        logger.setLevel(logging.DEBUG)
    case False:
        logger.setLevel(logging.INFO)

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("flask_app.log", mode="a", encoding="utf-8")

default_formater = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s (%(name)s): %(message)s",
            style = "%",
            datefmt="%Y-%m-%d %H:%M",
        )

console_handler.setFormatter(default_formater)
file_handler.setFormatter(default_formater)

logger.addHandler(console_handler)
logger.addHandler(file_handler)

logger.info("")
logger.info("---------------------")
logger.info("--- NOVA EXECUÇÃO ---")
logger.info("---------------------")
logger.info("")

thread = None
thread_lock = Lock()

app = Flask(__name__)
socketio = SocketIO(app)


@app.route("/")
def index():
    return render_template("index.html")


@app.route("/satellite")
def satellite():
    return render_template("satellite.html")


@socketio.on("connect")
def connect():
    print("Cliente conectado")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("disconnect")
def disconnect():
    print("Cliente desconectado", request.sid)


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def background_thread():
    log_path = "logs/log.csv"
    with open(log_path, "w") as log_file:

        log_file.write(
            f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n"
        )
    print("Thread started")
    while True:
        try:
            response = com.read_response()
            if not response:
                socketio.sleep(0.5)
                continue
            print(f"Recebido-> {response}")
            now = get_current_datetime()
            with open(log_path, "a") as log_file:
                log_file.write(f"{now},{response}\n")
            fields = response.split(",")
            (
                TEAM_ID,
                millis,
                count,
                altp,
                temp,
                umi,
                p,
                gp,
                gr,
                gy,
                ap,
                ar,
                ay,
                hora,
                data,
                alt,
                lat,
                lon,
                sat,
                pqd,
                rssi,
            ) = fields

            if TEAM_ID == "#100":

                socketio.emit(
                    "updateRocket",
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "altura": altp,
                        "satelites": sat,
                        "rssi": rssi,
                        "pqd": pqd,
                        "time": now,
                    },
                )

            if TEAM_ID == "#261":
                socketio.emit(
                    "updateSat",
                    {
                        "latitude": lat,
                        "longitude": lon,
                        "altura": altp,
                        "satelites": sat,
                        "temperatura": temp,
                        "umidade": umi,
                        "pressao": p,
                        "rssi": rssi,
                        "time": now,
                    },
                )

            socketio.sleep(0.5)

        except Exception as e:
            print(f"Erro em background_thread-> {e}")
            socketio.sleep(1)


def open_browser(port):
    webbrowser.open_new(f"http://localhost:{port}/")


if __name__ == "__main__":
    ports = list_ports()

    # if not ports:
        # print("Nenhuma porta serial encontrada.")
        # exit(1)

    intervalo_verificacao_portas = 1
    qtd_tentativas = 15

    while not ports and qtd_tentativas:
        logger.warning(f"Nenhuma serial encontrada, verificando novamente")
        time.sleep(intervalo_verificacao_portas)
        ports = list_ports()
        qtd_tentativas -= 1

    if not ports:
        logger.critical("Nenhuma serial encontrada, desligando")
        exit(-1)

    print("Portas seriais disponíveis:")
    for i, port in enumerate(ports):
        print(f"{i + 1}: {port}")
    selected_port = input("Selecione a porta serial (número): ")


    try:
        selected_port = ports[int(selected_port) - 1]
    except (IndexError, ValueError):
        print("Seleção inválida. Encerrando.")
        exit(1)

    print(f"Porta selecionada: {selected_port}")
    com = base_com(selected_port)
    port = 5000
    open_browser(port)
    socketio.run(app, host="0.0.0.0", port=port)

