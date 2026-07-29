#include <SPI.h>
#include <LoRa.h>
#include "LoraReceiver.h"
#include "config.h"

bool loraInit() {
    SPI.begin(LORA_SCK, LORA_MISO, LORA_MOSI, LORA_CS);
    LoRa.setPins(LORA_CS, LORA_RST, LORA_IRQ);

    if (!LoRa.begin(LORA_FREQUENCY)) {
        Serial.println("[LoRa] Falha na inicialização");
        return false;
    }

    LoRa.setSpreadingFactor(LORA_SF);
    LoRa.setSignalBandwidth(LORA_BW);
    LoRa.setCodingRate4(LORA_CR);
    LoRa.setTxPower(LORA_TX_POWER);
    LoRa.enableCrc();

    Serial.println("[LoRa] Inicializado OK");
    return true;
}

bool loraSend(const String& payload) {
    LoRa.beginPacket();
    LoRa.print(payload);
    bool ok = LoRa.endPacket();
    if (ok) Serial.println("[LoRa] TX: " + payload);
    else    Serial.println("[LoRa] Falha no envio");
    return ok;
}

int loraLastRSSI() {
    return LoRa.packetRssi();
}
