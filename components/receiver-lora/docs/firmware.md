# Receiver LoRa —Firmware

## Visao geral

Receiver LoRa do sistema de recuperacao Serra Rocketry. Recebe pacotes de
telemetria via radio LoRa (915 MHz) do satellite, preenche campos de hora/data
com GPS local, e retransmite via Serial (USB) no formato do protocolo Recovery
WebUI.

**Contexto**: O receiver fica no solo e precisa receber dados do satellite em voo
para alimentar o Recovery WebUI em tempo real. Pacotes perdidos e erros de parse
sao contados e logados na Serial para diagnostico.

## Arquitetura

```
Receiver LoRa
├── config.h               — Configuracoes (pinos, frequencia LoRa, baud rate)
├── main.cpp               — Setup + loop (recebe LoRa, parse, retransmite)
├── LoraReceiver.h/cpp     — Driver LoRa (modo RX continuo + TX para debug)
├── GpsModule.h/cpp        — Wrapper TinyGPSPlus (GPS local do receiver)
└── payload.h              — Formatacao do pacote CSV de 21 campos (protocolo)
```

## Fluxo de operacao

```
┌──────────────┐     LoRa 915MHz     ┌──────────────┐     USB Serial     ┌──────────────┐
│   Satellite  │ ──────────────────> │   Receiver   │ ─────────────────> │ Recovery     │
│   (TX)       │  pacote 19 campos   │   (RX)       │  pacote 21 campos  │ WebUI        │
└──────────────┘                     └──────────────┘                    └──────────────┘
                                            │
                                            │ GPS local
                                            │ (preenche hora/data)
                                            ▼
                                     ┌──────────────┐
                                     │  NEO-8M GPS  │
                                     └──────────────┘
```

### Loop principal

1. `gpsProcess()` — alimenta parser GPS local
2. `loraAvailable()` — verifica se ha pacote LoRa pronto
3. `loraReceive()` — le pacote (19 campos CSV)
4. `parseSatellitePacket()` — valida e extrai campos
5. `trackPacketCount()` — detecta pacotes perdidos (salto no count)
6. `gpsGetTimeData()` — obtem hora/data do GPS local
7. `buildProtocolPacket()` — monta pacote de 21 campos
8. `Serial.println()` — retransmite para o Recovery WebUI

## Formato dos Pacotes

### Satellite -> Receiver (19 campos, via LoRa)

```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,rssi
```

Campos `hora` e `data` sao omitidos do radio (economia de bytes). Campo `rssi`
e placeholder (-1).

### Receiver -> Recovery WebUI (21 campos, via Serial)

```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,rssi
```

Campos `hora` e `data` sao preenchidos pelo GPS local do receiver. Campo `rssi`
e o valor real medido pelo receiver (`LoRa.packetRssi()`).

## Comunicacao LoRa

| Parametro       | Valor     | Nota                           |
|-----------------|-----------|--------------------------------|
| Frequencia      | 915 MHz   | Americas/Brasil                |
| Sync Word       | 0xF3      | Deve bater com satellite       |
| Spreading Factor| 7         | SF7                            |
| Bandwidth       | 125 kHz   |                                |
| Coding Rate     | 4/5       |                                |
| TX Power        | 17 dBm    |                                |
| CRC             | habilitado|                                |

## Contagem de Pacotes Perdidos

O receiver rastreia o campo `count` do satellite para detectar pacotes perdidos:

- **Sem perda**: silencioso (nao polui a Serial)
- **Salto no count**: loga `[LOST] N pacote(s) perdido(s) — count X -> Y | total perdidos: Z`
- **Reset de count** (reboot do satellite): loga `[STATS] Count resetado — X -> Y`
- **Erro de parse**: loga `[STATS] Erro de parse #N` + estatisticas acumuladas
- **Primeiro pacote**: loga `[STATS] Primeiro pacote recebido — count=N`

Exemplo de log na Serial:

```
[LoRa] RX (RSSI=-67): #213,1205,42,150.50,25.30,45.20,1013.25,0.50,1.20,-0.30,0.10,0.20,9.80,150.00,-23.550500,-46.633300,8,0,-1
#213,1205,42,150.50,25.30,45.20,1013.25,0.50,1.20,-0.30,0.10,0.20,9.80,143523,14032026,150.00,-23.550500,-46.633300,8,0,-67

[LOST] 3 pacote(s) perdido(s) — count 45 -> 49 | total perdidos: 3
[STATS] Recebidos: 48 | Perdidos: 3 | Erros parse: 0 | Taxa perda: 6%
```

## Pinagem

| Pino | Funcao     | Componente       |
|------|------------|------------------|
| 2    | SPI MISO   | RFM95W MISO      |
| 3    | SPI MOSI   | RFM95W MOSI      |
| 4    | SPI SCK    | RFM95W SCK       |
| 5    | SPI CS     | RFM95W chip sel  |
| 6    | LoRa RST   | RFM95W reset     |
| 7    | LoRa IRQ   | RFM95W DIO0      |
| 20   | UART1 RX   | GPS NEO-8M TX    |
| 21   | UART1 TX   | GPS NEO-8M RX    |

## Configuracoes

Em `config.h`:

| Parametro       | Default | Descricao                    |
|-----------------|---------|------------------------------|
| `LORA_FREQUENCY`| 915E6   | Frequencia Hz                |
| `LORA_SYNC_WORD`| 0xF3    | Sync word                    |
| `LORA_SF`       | 7       | Spreading Factor             |
| `LORA_BW`       | 125E3   | Bandwidth Hz                 |
| `LORA_CR`       | 5       | Coding Rate (4/5)            |
| `LORA_TX_POWER` | 17      | Potencia TX dBm              |
| `GPS_BAUD`      | 9600    | Baud rate GPS                |
| `SERIAL_BAUD`   | 115200  | Baud rate Serial USB         |

## Build e Upload

```bash
cd receiver-lora/firmware/Receiver

# Build
pio run

# Upload
pio run -t upload --upload-port /dev/ttyACM0

# Serial monitor
pio device monitor -b 115200
```

## Antena

### Receiver: Yagi 3-5 elementos (915 MHz)

- Ganho: 7-10 dBi
- Polarizacao: vertical
- Beamwidth: 40-60o horizontal, 30-50o vertical
- Boom: ~13-26 cm
- Apontar na direcao do satellite (azimute) com elevacao de ~0-35o

### Satellite: Monopolo lambda/4 de fita metrica

- Comprimento: ~8 cm (lambda/4 em 915 MHz)
- Ganho: 2-5 dBi
- Polarizacao: vertical
- Montado no corpo do PocketQube, apontando para baixo
- Corpo metalico como counterpoise

### Link Budget estimado (1.5 km)

| Cenario              | Distancia max |
|----------------------|---------------|
| Free space           | 147 km        |
| Rural / vegetacao    | 21 km         |
| Suburban             | 6 km          |
| Suburban denso       | 2.4 km        |

## ADRs

### ADR-001: Receiver em modo RX continuo

**Status**: Aceito

**Contexto**: O receiver precisa receber pacotes do satellite a 5Hz sem perda.

**Decisao**: Usar `LoRa.receive()` modo continuo (nao polling com `parsePacket`). O
ISR do DIO0 acorda o loop para processar.

**Consequencias**:
- (+) Latencia minima entre recebimento e processamento
- (-) Consumo de energia maior (recepcao continua)
- (-) Impossivel transmitir enquanto recebe (nao e necessario)

### ADR-002: Hora/data preenchidos pelo receiver

**Status**: Aceito

**Contexto**: Transmitir hora/data do GPS do satellite via LoRa adiciona 2 campos
(~20 bytes) ao pacote.

**Decisao**: Omitir hora/data do pacote LoRa. O receiver preenche com dados do
seu GPS local. Se nao tiver fix, fica 0.

**Consequencias**:
- (+) Pacote ~20 bytes menor
- (+) Complexidade do satellite reduzida
- (-) Hora/data reflete o receiver, nao o satellite
- (-) Se receiver nao tem GPS fix, campos ficam 0

Na pratica, o `app.py` ja adiciona `NOW` (timestamp local) ao receber, entao a
informacao temporal esta presente independentemente.

## Referencias

- Repositorio: `recovery-webui/components/receiver-lora/`
- Protocolo completo: `recovery-webui/docs/protocol.md`
- Configuracao Yagi: `docs/hardware.md`
- LoRa SX1276 datasheet: https://www.semtech.com/products/wireless-rf/lora-transceivers/sx1276
