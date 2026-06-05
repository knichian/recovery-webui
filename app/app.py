from module import BaseCom, list_ports
from flask import Flask, jsonify, redirect, render_template, request, redirect
from flask_api import status
from flask_socketio import SocketIO
from threading import Lock
from datetime import datetime
import logging
import sys
import os


debug_mode: bool = False
simulation_mode: bool = False

# verificando os argumentos passados para cli
for option in sys.argv:
    # verificando se o modo debug foi solicitado 
    if option == "--debug":
        debug_mode = True
    # verificando se o modo simulação foi solicitado 
    if option == "--simulation":
        simulation_mode = True


# configurando loggers
app_logger = logging.getLogger("Web-App")
ws_logger = app_logger.getChild("WebSocket")
antenna_logger = app_logger.getChild("Antenna")

if debug_mode:
    app_logger.setLevel(logging.DEBUG)
else:
    app_logger.setLevel(logging.INFO)

current_day_date = datetime.now().strftime("%Y_%m_%d")
log_file_name = "webapp_log_{current_day_date}"
file_handler = logging.FileHandler(f"logs/{log_file_name}.log", mode="a", encoding="utf-8")
console_handler = logging.StreamHandler()

default_formater = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s (%(name)s): %(message)s",
            style = "%",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

console_handler.setFormatter(default_formater)
file_handler.setFormatter(default_formater)

app_logger.addHandler(console_handler)
app_logger.addHandler(file_handler)

app_logger.info("")
app_logger.info("---------------------")
app_logger.info("--- NOVA EXECUÇÃO ---")
app_logger.info("---------------------")
app_logger.info("")

if debug_mode:
    app_logger.debug("modo debug ativado!")


# interface serial
antenna_serial_configured: bool = False
antenna_serial = BaseCom(antenna_logger)


# aplicação flask
app: Flask = Flask(__name__)

if debug_mode:
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.config["TEMPLATES_AUTO_RELOAD"]


# websocket
socketio: SocketIO = SocketIO(app)
thread = None
thread_lock = Lock()


# flask Rotas
@app.get("/")
def index():
    if antenna_serial_configured:
        return redirect("/rocket")
    else:
        return redirect("/config")


# @app.route("/rocket")
@app.get("/rocket")
def rocket_monitor():
    if antenna_serial_configured:
        return render_template("rocket.html")
    else:
        return redirect("/config")


@app.get("/satellite")
def satellite_monitor():
    if antenna_serial_configured:
        return render_template("satellite.html")
    else:
        return redirect("/config")


@app.route("/config", methods=["GET", "POST"])
def serial_config():
    if request.method == "GET":
        return render_template("config.html")
    elif request.method == "POST":
        global antenna_serial_configured 

        data = request.form

        serial_port: str = data["serial"]
        baudrate: int = int(data["baudrate"])
        timeout: float = float(data["timeout"])

        antenna_serial.configure_serial(serial_port, baudrate, timeout)
        antenna_serial_configured = True

        app_logger.info("Configuração atualizada:")
        app_logger.info(f"{serial_port=}")
        app_logger.info(f"{baudrate=}")
        app_logger.info(f"{timeout=}")

        response = f'''
            Configuração Atualizada!
            {serial_port=}
            {baudrate=}
            {timeout=}
        '''

        return ( response, status.HTTP_202_ACCEPTED )
    else:
        message = "metodo não suportado"
        app_logger.error(message)
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
    app_logger.info("Cliente conectado")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("disconnect")
def disconnect():
    app_logger.info("Cliente desconectado")


# TODO: finish the system to configure the serial interface from the webapp
# TODO: verify efficience on writing the data to file

def background_thread():
    current_time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    data_out_file_path = f"data/data_{current_time_stamp}.csv"

    with open(data_out_file_path, "w") as data_out_file:
        data_out_file.write( f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n" )

    ws_logger.info("comunicação websocket iniciada")

    while True:
        try:
            response = antenna_serial.read_response()

            if not response:
                continue

            ws_logger.info(f"Recebido -> {response}")
            now = get_current_datetime()

            with open(data_out_file_path, "a") as data_out_file:
                data_out_file.write(f"{now},{response}\n")

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
            # socketio.sleep(1)
        except Exception as e:
            app_logger.error(f"Erro em background_thread -> {e}")
            socketio.sleep(1)


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


if __name__ == "__main__":

    if debug_mode == True :
        ports = list_ports()
        if ports:
            app_logger.debug("Portas seriais disponíveis:")
            for i, port in enumerate(ports):
                app_logger.debug(f"{i + 1}: {port}")
        else:
            app_logger.debug("Nenhuma porta serial encontrada")

    socketio.run( app, host="0.0.0.0", port=5000, debug=debug_mode, extra_files=[template_dir] )
