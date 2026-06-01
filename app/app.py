from module import *
from flask import Flask, jsonify, redirect, render_template, request, redirect
from flask_api import status
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
import logging
import sys
import os

debug_mode: bool = False

for option in sys.argv:
    if option == "--debug":
        debug_mode = True

template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')

logger = logging.getLogger("Flask-App")

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler("logs/flask_app.log", mode="a", encoding="utf-8")

default_formater = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s (%(name)s): %(message)s",
            style = "%",
            datefmt="%Y-%m-%d %H:%M:%S",
        )


if debug_mode:
    logger.setLevel(logging.DEBUG)
else:
    logger.setLevel(logging.INFO)


console_handler.setFormatter(default_formater)
file_handler.setFormatter(default_formater)


logger.addHandler(console_handler)
logger.addHandler(file_handler)


logger.info("")
logger.info("---------------------")
logger.info("--- NOVA EXECUÇÃO ---")
logger.info("---------------------")
logger.info("")


if debug_mode:
    logger.debug("modo debug ativado!")


thread = None
thread_lock = Lock()


app: Flask = Flask(__name__)
socketio: SocketIO = SocketIO(app)
com = None
# antenna_serial = None


if debug_mode:
    app.config["TEMPLATES_AUTO_RELOAD"]


@app.route("/")
def index():
    if com != None:
        return redirect("/config")
    else:
        return redirect("/rocket")


@app.route("/rocket")
def rocket():
    if com != None:
        return redirect("/config")
    else:
        return render_template("rocket.html")


@app.route("/satellite")
def satellite():
    if com != None:
        return render_template("satellite.html")
    else:
        return redirect("/config")


@app.route("/config", methods=["GET", "POST"])
def config():
    if request.method == "GET":
        return render_template("config.html")
    elif request.method == "POST":
        return ( "Configuração Atualizada!", status.HTTP_202_ACCEPTED )
    else:
        message = "metodo não suportado"
        logger.error(message)
        return ( message, status.HTTP_405_METHOD_NOT_ALLOWED )


@app.get("/config/fetch_serial")
def fetch_serial():

    # serial_list = list_ports()
    #
    # response = {
    #         "serial_list": serial_list
    #         }

    response = {
            "serial_list": [ "serial1", "serial2",  "serial3" ]
            }

    return jsonify(response)


@socketio.on("connect")
def connect():
    logger.info("Cliente conectado")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("disconnect")
def disconnect():
    logger.info("Cliente desconectado")


def background_thread():
    current_time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    log_path = f"data/data_{current_time_stamp}.csv"
    with open(log_path, "w") as log_file:

        log_file.write( f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n" )
    print("Thread started")
    while True:
        try:
            response = com.read_response()
            if not response:
                # socketio.sleep(1)
                continue
            logger.info(f"Recebido -> {response}")
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

            socketio.sleep(1)

        except Exception as e:
            logger.error(f"Erro em background_thread -> {e}")
            socketio.sleep(1)


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":

    if debug_mode == True :
        ports = list_ports()
        if ports:
            logger.debug("Portas seriais disponíveis:")
            for i, port in enumerate(ports):
                logger.debug(f"{i + 1}: {port}")
        else:
            logger.debug("Nenhuma porta serial encontrada")

    socketio.run( app, host="0.0.0.0", port=5000, debug=debug_mode, extra_files=[template_dir] )
