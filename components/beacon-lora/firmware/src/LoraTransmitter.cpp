#include <SPI.h>
#include <LoRa.h>
#include "LoraTransmitter.h"
#include "config.h"

static bool _loraReady = false;

bool loraInit() {
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_IRQ);

    if (!LoRa.begin(LORA_FREQUENCY)) {
        Serial.println("[LoRa] Falha na inicializacao");
        _loraReady = false;
        return false;
    }

    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setSignalBandwidth(LORA_BW);
    LoRa.setCodingRate4(LORA_CR);
    LoRa.setSyncWord(LORA_SYNC_WORD);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.enableCrc();

    _loraReady = true;
    Serial.print("[LoRa] TX OK (");
    Serial.print(LORA_FREQUENCY / 1E6, 0);
    Serial.print("MHz, SF");
    Serial.print(LORA_SF);
    Serial.print(", BW");
    Serial.print(LORA_BW / 1E3, 0);
    Serial.println("kHz)");
    return true;
}

bool loraSend(const String& payload) {
    if (!_loraReady) return false;

    LoRa.beginPacket();
    LoRa.print(payload);
    bool ok = (LoRa.endPacket() == 1);

    if (ok) {
        Serial.println("[LoRa] TX: " + payload);
    } else {
        Serial.println("[LoRa] Falha no envio");
    }
    return ok;
}

int loraLastRSSI() {
    return LoRa.packetRssi();
}
