#include <Arduino.h>
#include "config.h"
#include "LoraTransmitter.h"
#include "GpsModule.h"
#include "payload.h"

static uint32_t packetCount = 0;

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(400);
    Serial.println();
    Serial.println("=== Beacon LoRa — Simulador ===");
    Serial.print("TEAM_ID: ");
    Serial.println(TEAM_ID);
    Serial.println();

    gpsInit();

    if (!loraInit()) {
        Serial.println("[SYS] Falha critica no LoRa — travando");
        while (1) delay(1000);
    }

    Serial.println();
    Serial.println("[SYS] Beacon pronto — heartbeat a cada "
                   + String(TX_INTERVAL_MS) + "ms");
    Serial.println();
}

void loop() {
    gpsProcess();

    static uint32_t lastTx = 0;
    uint32_t now = millis();

    if (now - lastTx < TX_INTERVAL_MS) return;
    lastTx = now;

    GpsData gps = gpsGetData();

    BeaconData data = {0};
    data.millis = now;
    data.count  = packetCount++;

    data.alt = gps.altMeters;
    data.lat = gps.lat;
    data.lon = gps.lon;
    data.sat = (uint8_t)gps.satellites;

    String packet = buildBeaconPacket(TEAM_ID, data);

    loraSend(packet);

    Serial.print("[SYS] Heartbeat #");
    Serial.print(data.count);
    Serial.print(" | GPS: ");
    if (gps.valid) {
        Serial.print(gps.lat, 6);
        Serial.print(", ");
        Serial.print(gps.lon, 6);
        Serial.print(" (");
        Serial.print(gps.satellites);
        Serial.print(" sat)");
    } else {
        Serial.print("sem fix");
    }
    Serial.println();
}
