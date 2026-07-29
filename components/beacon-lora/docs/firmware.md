# Beacon LoRa — Simulador

## Visão Geral

Beacon LoRa simplificado, idêntico em hardware e software ao `receiver-lora`.
Apenas envia heartbeats periódicos via LoRa para testar a comunicação com o
receptor em solo.

## Hardware

Mesmo hardware do receiver:

| Componente | Função          | Interface |
|------------|-----------------|-----------|
| ESP32-C3   | Microcontrolador | -         |
| RFM95W     | Rádio LoRa      | SPI       |
| NEO-6M/7M/8M | GPS           | UART1     |

## Funcionamento

A cada `TX_INTERVAL_MS` (200ms = 5 Hz) o beacon transmite um pacote CSV de
19 campos via LoRa. Todos os campos de sensores (IMU, BME280) são enviados
como zero. Os únicos dados reais são:

- `millis` — timestamp local
- `count` — contador sequencial
- `alt`, `lat`, `lon`, `sat` — dados do GPS (se tiver fix)
- `rssi` — placeholder -1 (o receiver preenche o RSSI real)

## Formato do Pacote

```
TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,alt,lat,lon,sat,pqd,rssi
```

Exemplo com GPS sem fix:
```
#213,12345,1,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.00,0.000000,0.000000,0,0,-1
```

## Parâmetros LoRa

Devem bater com o `receiver-lora`:

| Parâmetro       | Valor    |
|-----------------|----------|
| Frequência      | 915 MHz  |
| Sync Word       | 0xF3     |
| Spreading Factor| 7        |
| Bandwidth       | 125 kHz  |
| Coding Rate     | 4/5      |
| TX Power        | 17 dBm   |

## Build e Upload

```bash
cd components/beacon-lora/firmware

pio run                      # build
pio run -t upload            # upload
pio device monitor -b 115200 # monitor serial
```
