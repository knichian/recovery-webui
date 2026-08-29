# Beacon LoRa

Beacon do mesh de trilateração do sistema de recuperação da Serra Rocketry.
Cada beacon escuta os pacotes do satellite (#213) via LoRa 915 MHz, mede o
RSSI do MESMO pacote e reporta ao receiver (posição GPS própria + RSSI +
referência do pacote). Com ≥3 ouvintes, o receiver trilatera a posição do
satellite quando o GPS dele falha/diverge.

> Documentação técnica completa: [docs/firmware.md](docs/firmware.md)
> (do receiver — descreve o mesh e o protocolo `#Bx`)

## Hardware

| Item   | Descrição                       |
|--------|---------------------------------|
| MCU    | ESP32-C3 DevKitM-1              |
| Rádio  | RFM95W (LoRa 915 MHz, SPI)      |
| GPS    | NEO-8M (UART1)                  |

**Atenção**: o módulo LoRa opera estritamente em 3.3 V — nunca ligue VCC no 5V.

### Pinagem (ESP32-C3)

| Pino | Função    | Componente    |
|------|-----------|---------------|
| 4    | SPI SCK   | RFM95W SCK    |
| 3    | SPI MOSI  | RFM95W MOSI   |
| 2    | SPI MISO  | RFM95W MISO   |
| 5    | SPI CS    | RFM95W NSS/CS |
| 6    | LoRa RST  | RFM95W RESET  |
| 7    | LoRa IRQ  | RFM95W DIO0   |
| 20   | UART1 RX  | GPS TX        |
| 21   | UART1 TX  | GPS RX        |

> **Pendência**: o receiver já foi migrado para o ESP32 DevKit V1 (DOIT) — se
> os beacons também forem montados no DevKit V1, os pinos mudam
> (SPI 18/23/19, RST=14, DIO0=2, GPS 16/17) e este README + `config.h`
> precisam de atualização.

## Identidade do beacon

Cada unidade é gravada com um ID único (`B1`..`B8`) antes do deploy. Editar
`BEACON_ID` em `firmware/include/config.h`:

```c
#define BEACON_ID "B1"   // unico por beacon
```

O receiver rastreia até 8 beacons (`TRILAT_MAX_BEACONS = 8`) por esse ID.

## Requisitos

- [PlatformIO Core](https://docs.platformio.org/en/latest/core/index.html)
  (CLI) ou a extensão PlatformIO no VS Code. Instalação via pip/pyenv:

  ```bash
  pip install -U platformio
  ```

- Cabo USB (o C3 usa porte USB nativo — CDC habilitado no build)

## Build

```bash
cd components/beacon-lora/firmware
pio run
```

## Upload

```bash
# Porta tipica no Linux para o C3: /dev/ttyACM0
pio run -t upload --upload-port /dev/ttyACM0
```

## Monitor serial

```bash
pio device monitor -b 115200
```

## Testar

### 1. Teste em banco (sem rádio)

1. Conecte via USB e abra o monitor.
2. Confirme GPS fix ao céu aberto (1–5 min no primeiro ligamento). Sem fix o
   beacon continua operando, mas seus reports têm `gpsv=0` e são **rejeitados
   pelo cesto de trilateração** do receiver.
3. Verifique o log de reports periódicos.

### 2. Teste no mesh (com receiver + satellite de bancada)

1. Grave cada beacon com `BEACON_ID` distinto.
2. Configure um transmissor de bancada com os **mesmos parâmetros de rádio**
   do `config.h` (915 MHz, sync word `0xF3`, SF7, BW 125 kHz, CR 4/5) e o
   formato de pacote do satellite (`#213,...#`).
3. No monitor do **receiver**, o beacon deve aparecer como ativo e ouvindo:

   ```
   [MESH] Beacons ativos: 1/8 | ouvindo o satellite: 1 | ultimo pkt: #4521
   ```

4. Com receiver + 2 beacons ouvindo o mesmo pacote, o cesto fecha e o receiver
   emite o `#213` corrigido:

   ```
   [TRI] pkt#4523 corrigido: -21.775551,-48.175565 | ouvintes=3 | residuo=112.3m
   ```

5. Sem satellite por mais de `HEARTBEAT_INTERVAL_MS` (2 s), o beacon envia
   heartbeat (`sat_count=0`) — no receiver, aparece como "ativo" mas não
   "ouvindo".

### 3. Teste de anti-colisão (múltiplos beacons)

Com 3+ beacons ligados juntos, o jitter aleatório de TX
(`TX_JITTER_MIN_MS`/`TX_JITTER_MAX_MS` = 15–120 ms) evita colisão. Validar no
receiver: reports de todos os beacons chegando (tabela de beacons atualizada)
e taxa de parse baixa nos `[STATS]`.

## Como o beacon opera

- Ouve o satellite continuamente; a cada pacote `#213` recebido, agenda um
  report `#Bx` com jitter aleatório (intervalo mínimo de 250 ms
  — `REPORT_MIN_INTERVAL_MS`)
- O report carrega: ID, uptime, `count`/`millis` do pacote do satellite ouvido,
  posição GPS própria, RSSI medido e flag de fix
- É o par `sat_count`/`sat_millis` que permite ao receiver garantir que todos
  os ouvintes mediram o **mesmo** pacote (idade ≤ 1,5 s)

## Estrutura do projeto

```
firmware/
├── platformio.ini          — Config do PlatformIO (env, libs, flags)
├── include/                — config.h e headers
└── src/                    — main.cpp, LoraTransmitter, GpsModule
```

Dependências gerenciadas pelo PlatformIO (instaladas automaticamente no build):

- `sandeepmistry/LoRa @ ^0.8.0`
- `mikalhart/TinyGPSPlus @ ^1.0.3`

## Solução de problemas

| Sintoma | Causa provável / correção |
|---------|---------------------------|
| `LoRa init failed` | Fiação divergente do `config.h`, falta de antena, módulo em 5V |
| Receiver não lista o beacon como ativo | `BEACON_ID` duplicado, frequência/sync word divergentes, GPS sem fix (`gpsv=0`) |
| Reports colidindo no receiver | Jitter desativado/alterado; restore `TX_JITTER_*` no `config.h` |
| Upload trava em `Connecting...` | Feche o monitor serial; no C3, segure BOOT durante o connect |
| Porta não aparece | Instale o driver USB-UART; verifique `ls /dev/ttyUSB* /dev/ttyACM*` |
| RSSI sempre -127 nos reports | Antena desconectada ou satellite fora dos parâmetros de rádio |