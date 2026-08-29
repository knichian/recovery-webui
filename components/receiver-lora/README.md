# Receiver LoRa

Receiver de solo do sistema de recuperação da Serra Rocketry. Recebe telemetria
via LoRa (915 MHz) do satellite (#213) e dos foguetes (#11/#51), preenche
hora/data com GPS local e retransmite pela Serial (USB) no formato do protocolo
Recovery WebUI. Também é o nó central do mesh de trilateração por RSSI.

> Documentação técnica completa (arquitetura, protocolos, ADRs, simulação de
> precisão): [docs/firmware.md](docs/firmware.md)

## Hardware

| Item        | Descrição                                    |
|-------------|----------------------------------------------|
| MCU         | ESP32 DevKit V1 (DOIT)                       |
| Rádio       | RFM95W (LoRa 915 MHz, SPI)                   |
| GPS         | NEO-8M (UART2)                               |
| Antena      | Yagi 3–5 elementos, 915 MHz (ver firmware.md)|

**Atenção**: o módulo LoRa opera estritamente em 3.3 V — nunca ligue VCC no 5V.

### Pinagem

| Pino | Função    | Componente      |
|------|-----------|-----------------|
| 18   | SPI SCK   | RFM95W SCK      |
| 23   | SPI MOSI  | RFM95W MOSI     |
| 19   | SPI MISO  | RFM95W MISO     |
| 5    | SPI CS    | RFM95W NSS/CS   |
| 14   | LoRa RST  | RFM95W RESET    |
| 2    | LoRa IRQ  | RFM95W DIO0     |
| 16   | UART2 RX  | GPS TX          |
| 17   | UART2 TX  | GPS RX          |

## Requisitos

- [PlatformIO Core](https://docs.platformio.org/en/latest/core/index.html)
  (CLI) ou a extensão PlatformIO no VS Code. Instalação via pip/pyenv:

  ```bash
  pip install -U platformio
  ```

- Cabo USB (o DevKit V1 usa chip USB-UART; porte USB nativo não é usado)

## Build

```bash
cd components/receiver-lora/firmware

# Compilar (env:esp32doit-devkit-v1)
pio run
```

## Upload

```bash
# Porta tipica no Linux: /dev/ttyUSB0 (ou /dev/ttyUSB1)
pio run -t upload --upload-port /dev/ttyUSB0
```

Se a porta estiver ocupada por um monitor serial, feche-o antes. Se o upload
falhar em `Connecting........_____`, segure o botão **BOOT** da placa durante
a conexão (raro; geralmente necessário só na primeira gravação ou após um
firmware que travou o UART).

## Monitor serial

```bash
pio device monitor -b 115200
```

Saída esperada no boot:

```
[GPS] aguardando fix...
[LoRa] RX iniciado em 915 MHz
[LoRa] RX (RSSI=-67): #213,1205,42,...
[MESH] Beacons ativos: 3/3 | ouvindo o satellite: 3 | ultimo pkt: #4521
```

Logs de diagnóstico: `[LOST]` (pacotes perdidos), `[STATS]` (taxa de perda e
erros de parse), `[MESH]` (saúde do mesh de beacons), `[TRI]` (correção de
trilateração aplicada).

## Testar

### 1. Teste em banco (sem rádio)

1. Conecte a placa via USB e abra o monitor serial (`pio device monitor -b 115200`).
2. Verifique no boot que não há mensagens de erro de inicialização.
3. Se o GPS estiver conectado, aguarde fix ao céu aberto (1–5 min no primeiro
   ligamento, depois segundos). Sem GPS conectado o firmware segue operando —
   os campos `hora`/`data` saem como 0.

### 2. Teste de recepção LoRa (loopback/ponto a ponto)

1. Monte o circuito da pinagem acima e verifique a antena no RFM95W **antes de
   energizar** (transmitir sem antena danifica o PA).
2. Use um segundo dispositivo (beacon ou satellite de bancada) configurado com
   os **mesmos parâmetros de rádio** — eles devem bater com o transmissor real:
   frequência 915 MHz, sync word `0xF3`, SF7, BW 125 kHz, CR 4/5
   (`include/config.h`).
3. Transmissor de bancada enviando o formato `#213,...#` (18 campos) deve
   produzir no monitor:

   ```
   [LoRa] RX (RSSI=-67): #213,1205,42,150.50,25.30,45.20,...
   ```

4. Pausar o transmissor e retomar com `count` adiantado valida o detector de
   pacotes perdidos:

   ```
   [LOST] 3 pacote(s) perdido(s) — count 45 -> 49 | total perdidos: 3
   ```

### 3. Teste do mesh de trilateração

1. Ligue pelo menos 2 beacons além do receiver (mínimo de
   `TRILAT_MIN_LISTENERS = 3` ouvintes), todos com GPS fix e ouvindo o mesmo
   satellite.
2. O cesto fecha e o receiver emite o `#213` com lat/lon corrigida:

   ```
   [TRI] pkt#4523 corrigido: -21.775551,-48.175565 | ouvintes=4 | residuo=112.3m
   ```

3. Sem beacons suficientes, o pacote sai com o GPS cru do satellite após a
   janela de 900 ms (`TRILAT_BASKET_WAIT_MS`) — comportamento de fallback
   esperado.
4. Resíduo > 1500 m (`TRILAT_MAX_RESIDUAL_M`) também cai no GPS cru (solução
   LSQ descartada).

### 4. Teste de integração com o Recovery WebUI

1. Conecte o receiver à máquina que roda a WebUI e identifique a porta:

   ```bash
   ls /dev/ttyUSB*
   ```

2. Aponte a WebUI para a porta serial — o receiver emite o formato v2.0
   (24 campos, `TEAM_ID,millis,...,rssi`) pela Serial a cada pacote recebido.
3. Valide na interface que os pacotes aparecem com hora/data preenchidas pelo
   GPS local do receiver.

## Configuração rápida (`include/config.h`)

| Parâmetro            | Default | Descrição                                  |
|----------------------|---------|--------------------------------------------|
| `LORA_FREQUENCY`     | 915E6   | Frequência em Hz (915 MHz Brasil)          |
| `LORA_SYNC_WORD`     | 0xF3    | Deve bater com o transmissor               |
| `TRILAT_MIN_LISTENERS`| 3      | Ouvintes mínimos p/ fechar o cesto         |
| `TRILAT_TX_POWER_DBM`| 20      | Potência TX do satellite (link budget RSSI)|

A lista completa de parâmetros de trilateração está em
[docs/firmware.md](docs/firmware.md#trilateracao--parametros-configh).

## Estrutura do projeto

```
firmware/
├── platformio.ini          — Config do PlatformIO (env, libs, flags)
├── partitions.csv          — Tabela de partições
├── include/                — config.h e headers
├── src/                    — main.cpp, LoraReceiver, GpsModule, Trilateration
└── lib/                    — Bibliotecas locais (se houver)
```

Dependências gerenciadas pelo PlatformIO (instaladas automaticamente no build):

- `sandeepmistry/LoRa @ ^0.8.0`
- `mikalhart/TinyGPSPlus @ ^1.0.3`

## Solução de problemas

| Sintoma | Causa provável / correção |
|---------|---------------------------|
| `LoRa init failed` | Fiação divergente do `config.h`, falta de antena, módulo alimentado em 5V |
| RSSI sempre -127 / nada recebido | Sync word ou frequência diferentes do transmissor; antena desconectada |
| Upload trava em `Connecting...` | Feche o monitor serial; segure BOOT durante o connect |
| Porta não aparece | Instale o driver CP210x/CH340 conforme o chip USB-UART da sua placa |
| Hora/data = 0 | GPS sem fix — leve ao céu aberto e aguarde |