from flask import Flask, render_template, request, redirect, Response, jsonify
from datetime import datetime
from flask_socketio import SocketIO
from threading import Lock, Thread
from module import BaseCom, FakeCom
# from datetime import datetime
# import webbrowser
import logging
import time
import sys
import os
import subprocess
from typing import Callable # from enum import global_enum_repr
from simple_term_menu import TerminalMenu, main
from flask_api import status

# variaves que definem modos de funcionamento
debug_mode: bool = False
simulation_mode: bool = False
cli_mode: bool = False


# variaveis de funcionalidade para o cli_mode
cli_display_data_flag: bool = False
cli_record_data_flag = False
cli_thread = None # pyright: ignore
cli_thread_lock = Lock()
cli_thread_loop_write_interval_s: float = 0.5 # define o intervalo de gravação no CSV


# verificando os argumentos passados para cli
for option in sys.argv:
    # verificando se o modo debug foi solicitado 
    if option == "--help":
        cli_help_message = """
Opções:
    --help
    --debug
    --cli
    --simulation
        """
        print(cli_help_message)
        sys.exit(0)
    if option == "--debug":
        debug_mode = True
    # verificando se o modo simulação foi solicitado 
    if option == "--simulation": # TODO: consider changing to "--synth"
        simulation_mode = True
    # verificando se usa CLI
    if option == "--cli":
        cli_mode = True


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

console_handler = logging.StreamHandler()
file_handler = logging.FileHandler(f"logs/{log_file_name}.log", mode="a", encoding="utf-8")

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

if simulation_mode:
    main_logger.debug("modo simulação ativado!")

# interface serial
antenna_serial_configured: bool = False


# thread & lock para funcionamento do websocket
thread = None # thread para rodar o funcionamento do websocket sem bloquear a tread principal da aplicação
thread_lock = Lock() # thread-lock para bloquear o acesso de outras treads as variaveis que a thread do websocket está usando


# webapp
app: Flask = Flask(__name__) # aplicação flask
socketio: SocketIO = SocketIO(app) # websocket


if debug_mode:
    template_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    app.config["TEMPLATES_AUTO_RELOAD"] # ativa o hot-reload do flask caso esteja em debug-mode
else:
    template_dir = ()


if simulation_mode:
    antenna_serial = FakeCom(antenna_logger)
else: 
    antenna_serial = BaseCom(antenna_logger)


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
    port_list = antenna_serial.get_port_options()
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
    main_logger.info("Cliente desconectado", request.sid) # pyright: ignore


def get_current_datetime():
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def background_thread():
    ws_logger.info("comunicação websocket iniciada")

    current_time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    data_out_file_name = f"data_{current_time_stamp}.csv"
    data_out_file_path = f"data/{data_out_file_name}"

    with open(data_out_file_path, "w") as data_out_file:
        data_out_file.write( f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n" )

    ws_logger.info(f"arquivo de captura de dado {data_out_file_name} criado")

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

            socketio.sleep(0.5) # pyright: ignore

        except Exception as e:
            main_logger.error(f"Erro em background_thread -> {e}")
            socketio.sleep(0.5) # pyright: ignore


# def open_browser(port):
#     webbrowser.open_new(f"http://localhost:{port}/")


def cli_clear():
    subprocess.call("clear" if os.name == "posix" else "cls")


def cli_configure_serial_select_port() -> ( Callable | None ):

    # ports: list = antenna_serial.list_ports()
    ports: list = antenna_serial.get_port_options()
    no_change_option: str = "Não mudar"

    menu_title = f"Selecione a porta: {'(nenhuma porta encontrada)' if not ports else ''}"

    options: list = ports if ports else []
    options.append(no_change_option)

    menu = TerminalMenu(options, title=menu_title)

    chosen_index = menu.show()

    if options[chosen_index] != no_change_option: # pyright: ignore
        antenna_serial.set_port(options[chosen_index]) # pyright: ignore

    return cli_configure_serial


def cli_configure_serial_select_baudrate() -> ( Callable | None ):

    baudrates: list = antenna_serial.get_baudrate_options()

    menu_title = "Selecione o baudrate:"
    menu_options = [ str(option) for option in baudrates]
    no_change_option: str = "Não mudar"

    menu_options.append(no_change_option)

    menu = TerminalMenu(menu_options, title=menu_title)

    chosen_index = menu.show()

    if menu_options[chosen_index] != no_change_option: # pyright: ignore
        antenna_serial.set_baudrate(int(menu_options[chosen_index])) # pyright: ignore
    
    return cli_configure_serial


def cli_configure_serial_select_timeout() -> ( Callable | None ):
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


def cli_configure_serial() -> ( Callable | None ):
    if antenna_serial.check_connected(): # bloqueia a edição da configuração serial se a conexão estiver ativa
        return cli_main_menu
    else:
        menu_title = f"Configuração Serial:"
        
        menu_options = [
                "Selecionar porta",
                "Selecionar baudrate",
                "Selecionar timeout",
                "Finalizar edição"
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


# callback para thread-secundaria que registra os dado, e se exibir no terminal se selecionado
def cli_record_serial_data_thread() -> None:

    main_logger.info("thread de captura de dados inicializada")

    # variaveis de passagem que controlam a thread-secundaria a partir da thread-principal
    global cli_record_data_flag # variavel de passagem que controla o loop de captura de dados
    global cli_display_data_flag # variavel de passagem controla a exibição das leituras no terminal (exibe caso esteja na tela de monitoramento)
    
    # logica principal da thread-secundaria
    global cli_thread_lock
    global cli_thread_loop_write_interval_s

    # definição do arquivo de saida para a coleta de dados
    current_time_stamp = datetime.now().strftime("%Y_%m_%d_%H_%M_%S")
    data_out_file_name = f"data_{current_time_stamp}" 
    data_out_file_extention = "csv"
    data_out_file_name_full = f"{data_out_file_name}.{data_out_file_extention}" 
    data_out_file_path = f"data/{data_out_file_name_full}" 

    with open(data_out_file_path, "w") as data_out_file: # cria o arquivo CSV de para captura de dado desta sessão
        data_out_file.write( f"NOW,TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi\n" )     # escreve o cabeçalho na primeira linha do CSV

    while cli_record_data_flag: # loop da captura de dados

        response = antenna_serial.read_response() # lê 1 "pacote" enviado pela antena

        if not response: # testa se conseguiu receber o pacote, caso não, reinicia o ciclo e tenta ler de novo
            continue

        now = get_current_datetime() # pega o horario atual
        
        with open(data_out_file_path, "a") as data_out_file: 
            data_out_file.write(f"{now},{response}\n") # grava o pacote no CSV, anexado(prefixado) com a data que a leitura foi capturada

        if cli_display_data_flag: # exibe no terminal os dados ... caso esteja na tela de     
            print(f"Recebido -> {now},{response}")

        time.sleep(cli_thread_loop_write_interval_s)
        
    main_logger.info("thread de captura de dados finalizada")
    return None


def cli_monitor_serial_data():
    if antenna_serial.check_connected():
        cli_clear() # limpa o terminal para exibir os dados
        global cli_display_data_flag
        cli_display_data_flag = True
        input("Pressione <Enter> para Sair!\n\n")
        cli_display_data_flag = False
    else:
        main_logger.error("conexão serial fechada, impossivel monitorar")
    return cli_main_menu


def cli_serial_on() -> ( Callable | None ):
    try:
        # inicia a conexão serial
        antenna_serial.open()

        # inicia a captura de dados
        global cli_thread 
        global cli_record_data_flag
        cli_thread = Thread( target=cli_record_serial_data_thread, daemon=True ) # cria a Thread de captura de dados
        cli_record_data_flag = True # ativa o loop dentro da Thread de captura de dados
        cli_thread.start() # inicia a Thread de captura de dados

    except:
        main_logger.error("Problema em abrir conexão com antena")

    return cli_main_menu


def cli_serial_off() -> ( Callable | None ):
    try:

        # finaliza a captura de dados
        global cli_record_data_flag
        cli_record_data_flag = False # fecha a Thread de captura de dados

        # finaliza a conexão serial
        antenna_serial.close() 

    except:

        main_logger.error("Problema em fechar conexão com antena")
        sys.exit(1)

    return cli_main_menu


def cli_main_menu() -> ( Callable | None ):

    # limpar terminal
    cli_clear()

    # menu principal
    serial_connection_status = antenna_serial.check_connected()

    main_menu_title = f'''
    Menu Principal:
        Port -> {"indefinida" if (antenna_serial.get_port() == None) else antenna_serial.get_port()}
        Baudrate -> {antenna_serial.get_baudrate()} bauds
        Timeout -> {antenna_serial.get_timeout()} sec

        Status Serial -> {"conectado" if antenna_serial.check_connected() else "desconectado"}
        Captura de dados -> {"ativada" if cli_record_data_flag else "desativada"}
        Intervalo de captura -> {cli_thread_loop_write_interval_s} sec

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
        case 0: # atualiza os status na tela principal do menu
            return cli_main_menu
        case 1:   # ativa ou desativa a conexão serial, dependendo do estado atual
            match serial_connection_status:
                case True:
                    return cli_serial_off
                case False:
                    return cli_serial_on
        case 2:  # configura a conexão serial (porta, baudrate, timeout)
            return cli_configure_serial
        # TODO: finish this function
        case 3:  # exibe os dado sendo capturados no terminal (incompleta...)
            if antenna_serial.check_connected():
                return cli_monitor_serial_data
            else:
                return cli_main_menu
        case 4: # fecha a aplicação
            main_logger.info("CLI app finalizado")
            return None
        case _: # opção inesperada, fecha a aplicação e marca um erro nos logs
            main_logger.critical("Erro em menu CLI!")
            return None


if __name__ == "__main__":

    if cli_mode:
        next_state: ( Callable | None ) = cli_main_menu()

        while next_state:
            next_state = next_state()

    else:
        socketio.run( app, host="0.0.0.0", port=5000, debug=debug_mode, extra_files=[template_dir] )

