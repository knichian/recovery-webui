from typing import Callable

from module import BaseCom, FakeCom
from flask import Flask, jsonify, redirect, render_template, request, redirect
from flask import Response
from flask import request
from flask_api import status
from flask_socketio import SocketIO
from threading import Lock, Thread
from datetime import datetime
from simple_term_menu import TerminalMenu
import logging
import sys
import os
import subprocess
import pygame

pygame.init()

debug_mode: bool = False
simulation_mode: bool = False
cli_mode: bool = False

# verificando os argumentos passados para cli
for option in sys.argv:
    # verificando se o modo debug foi solicitado 
    if option == "--debug":
        debug_mode = True
    # verificando se o modo simulação foi solicitado 
    if option == "--simulation":
        simulation_mode = True
    # verificando se usa CLI
    if option == "--cli":
        cli_mode = True
        # pygame.init()

# configurando loggers
main_logger = logging.getLogger("Cli_App") if cli_mode else logging.getLogger("WebApp")
ws_logger = main_logger.getChild("WebSocket")
antenna_logger = main_logger.getChild("Antenna")

if debug_mode:
    main_logger.setLevel(logging.DEBUG)
else:
    main_logger.setLevel(logging.INFO)

current_day_date = datetime.now().strftime("%Y_%m_%d")
log_file_name = f"webapp_log_{current_day_date}"
file_handler = logging.FileHandler(f"logs/{log_file_name}.log", mode="a", encoding="utf-8")
console_handler = logging.StreamHandler()

default_formater = logging.Formatter(
            "[%(asctime)s] %(levelname)-8s (%(name)s): %(message)s",
            style = "%",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

console_handler.setFormatter(default_formater)
file_handler.setFormatter(default_formater)

if not cli_mode: main_logger.addHandler(console_handler)
main_logger.addHandler(file_handler)

main_logger.info("")
main_logger.info("---------------------")
main_logger.info("--- NOVA EXECUÇÃO ---")
main_logger.info("---------------------")
main_logger.info("")

if debug_mode:
    main_logger.debug("modo debug ativado!")


# interface serial
antenna_serial_configured: bool = False

if simulation_mode:
    antenna_serial = FakeCom(antenna_logger)
else: 
    antenna_serial = BaseCom(antenna_logger)

# aplicação flask
app: Flask = Flask(__name__)

if debug_mode:
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.config["TEMPLATES_AUTO_RELOAD"]
else:
    template_dir = ()


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


@app.get("/config")
def serial_config():
    return render_template("serial_config.html")


# configurar serial pela webui
@app.get("/api/get_serial_ports")
def get_serial_ports():
    port_list = antenna_serial.list_ports()
    data = { "ports_avaliable": port_list }
    return jsonify(data)


@app.get("/api/get_baudrates")
def get_baudrates():
    baudrate_list = antenna_serial.serial.BAUDRATES
    data = { "baudrate_list": baudrate_list }
    return jsonify(data)


@app.post("/api/set_serial_config")
def set_serial_config():
    json = request.get_json()
    data = json["serial_configs"]

    new_port = data["port"]
    new_baurate = data["baudrate"]
    new_timeout = data["timeout"]

    antenna_serial.set_port(new_port)
    main_logger.info(f"Porta serial configurada para: {new_port}")
    antenna_serial.set_baudrate(new_baurate)
    main_logger.info(f"Baudrate configurado para: {new_baurate}")
    antenna_serial.set_timeout(new_timeout)
    main_logger.info(f"Timeout configurado para: {new_timeout}")

    return Response("", status.HTTP_201_CREATED)


# conexão websocket
@socketio.on("connect")
def connect():
    main_logger.info("Cliente conectado")
    global thread
    with thread_lock:
        if thread is None:
            thread = socketio.start_background_task(background_thread)


@socketio.on("disconnect")
def disconnect():
    main_logger.info("Cliente desconectado")


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

            ws_logger.debug(f"Recebido -> {response}")
            now = get_current_datetime()

            with open(data_out_file_path, "a") as data_out_file:
                data_out_file.write(f"{now},{response}\n")

            fields = response.split(",")

            TEAM_ID = fields[0]
            # millis =  fields[1]
            # count =   fields[2]
            altp =    fields[3]
            temp =    fields[4]
            umi =     fields[5]
            p =       fields[6]
            # gp =      fields[7]
            # gr =      fields[8]
            # gy =      fields[9]
            # ap =      fields[10]
            # ar =      fields[11]
            # ay =      fields[12]
            # hora =    fields[13]
            # data =    fields[14]
            # alt =     fields[15]
            lat =     fields[16]
            lon =     fields[17]
            sat =     fields[18]
            pqd =     fields[19]
            rssi =    fields[20]

            match TEAM_ID:
                case "#100":
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

                case "#261":
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

                case _:
                    main_logger.error(f"TEAM_ID não identificado: {TEAM_ID}")

            # socketio.sleep(1)

        except Exception as e:
            main_logger.error(f"Erro em background_thread -> {e}")
            socketio.sleep(1)


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def cli_clear():
    subprocess.call("clear" if os.name == "posix" else "cls")


def cli_configure_serial_select_port():

    ports: list = antenna_serial.list_ports()
    no_change_option: str = "Não mudar"

    menu_title = f"Selecione a porta: {'(nenhuma porta encontrada)' if not ports else ''}"

    options: list = ports if ports else []
    options.append(no_change_option)

    menu = TerminalMenu(options, title=menu_title)

    chosen_index = menu.show()

    if options[chosen_index] != no_change_option: # pyright: ignore
        antenna_serial.set_port(options[chosen_index]) # pyright: ignore

    return cli_configure_serial


def cli_configure_serial_select_baudrate():

    baudrates: list = antenna_serial.get_baudrates()

    menu_title = "Selecione o baudrate:"
    menu_options = [ str(option) for option in baudrates]
    no_change_option: str = "Não mudar"

    menu_options.append(no_change_option)

    menu = TerminalMenu(menu_options, title=menu_title)

    chosen_index = menu.show()

    if menu_options[chosen_index] != no_change_option: # pyright: ignore
        antenna_serial.set_baudrate(int(menu_options[chosen_index])) # pyright: ignore
    
    return cli_configure_serial


def cli_configure_serial_select_timeout():
    # TODO: make a menu function to select the serial timeout

    menu_title = "Selecione o timeout:"
    timeouts = [ 0, 0.25, 0.5, 1.0, 2.0, 2.5, 5.0, 7.5, 10 ] 
    menu_options = [ str(option) for option in timeouts]
    no_change_option: str = "Não mudar"

    menu_options.append(no_change_option)

    menu = TerminalMenu(menu_options, title=menu_title)

    chosen_index = menu.show()

    if menu_options[chosen_index] != no_change_option: # pyright: ignore
        antenna_serial.set_timeout(float(menu_options[chosen_index])) # pyright: ignore
    
    return cli_configure_serial


def cli_configure_serial():
    # TODO: make a menu function to configure the serial
    menu_title = f"Configuração Serial:"
    
    menu_options = [
            "Selecionar porta",
            "Selecionar baudrate",
            "Selecionar timeout",
            "Sair da configuração"
            ]

    menu = TerminalMenu(menu_options, title=menu_title)
    menu_chosen_index = menu.show()

    match menu_chosen_index:
        case 0: 
            return cli_configure_serial_select_port
        case 1: 
            return cli_configure_serial_select_baudrate
        case 2: 
            return cli_configure_serial_select_timeout
        case 3:
            return cli_main_menu


def cli_record_serial_data(): # TODO: make this function...

    current_time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    data_out_file_path = f"data/data_{current_time_stamp}.csv"

    with open(data_out_file_path, "w") as data_out_file:
        data_out_file.write( f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n" )

    while True:

        events = pygame.event.get()

        for event in events:
            if event.type == pygame.KEYDOWN :
                if (event.key == pygame.K_q) or (event.key == pygame.K_ESCAPE):
                    return cli_main_menu

        response = antenna_serial.read_response()

        if not response: continue

        now = get_current_datetime()
        
        with open(data_out_file_path, "a") as data_out_file:
            data_out_file.write(f"{now},{response}\n")
            print(f"Recebido -> {now},{response}")
            
        # return cli_main_menu


def cli_serial_on():
    try:
        antenna_serial.open()

    except:
        main_logger.error("porta serial ocupada")
    return cli_main_menu


def cli_serial_off():
    antenna_serial.close()
    return cli_main_menu


def cli_main_menu() -> Callable | None:

    # limpar terminal
    cli_clear()

    # menu principal
    serial_connection_status = antenna_serial.check_connected()

    main_menu_title = f'''
    Menu Principal:
        Port -> {"indefinida" if (antenna_serial.serial.port == None) else antenna_serial.serial.port}
        Baudrate -> {antenna_serial.serial.baudrate}
        Timeout -> {antenna_serial.serial.timeout}
        Status -> {"conectado" if antenna_serial.check_connected() else "desconectado"}

    '''
    main_menu_options = [
            "Atualizar status da serial",
            ("Desativar serial" if serial_connection_status else "Ativar serial"),
            "Editar configurações da serial",
            "Monitorar serial",
            "Sair da aplicação"
            ]

    main_menu = TerminalMenu(main_menu_options, title=main_menu_title)
    main_menu_chosen_index = main_menu.show()
    
    match main_menu_chosen_index:
        case 0:
            return cli_main_menu
        case 1:   # activate/deactivate serial cli option
            match serial_connection_status:
                case True:
                    return cli_serial_off
                case False:
                    return cli_serial_on
        case 2:  # configure cli option
            # TODO: make the function to configure the antenna
            return cli_configure_serial
        case 3:  # monitor cli option
            # TODO: figure out how to use pygame to get real time keyboard input
            if antenna_serial.check_connected():
                return cli_record_serial_data
            else:
                return cli_main_menu
        case 4:   # quit option
            main_logger.info("CLI app finalizado")
            return None
        case _:
            main_logger.critical("Erro em menu CLI!")
            return None


if __name__ == "__main__":

    if cli_mode:
        # TODO: make cli interface
        # TODO: make a state machine to power the cli interface
        next_state: ( Callable | None ) = cli_main_menu()

        while next_state:
            next_state = next_state()

    else:
        socketio.run( app, host="0.0.0.0", port=5000, debug=debug_mode, extra_files=[template_dir] )

