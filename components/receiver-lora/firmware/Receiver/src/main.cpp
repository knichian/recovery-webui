#include <Arduino.h>
#include "config.h"
#include "Buzzer.h"
#include "GpsModule.h"
#include "LoraReceiver.h"
#include "payload.h"

static uint32_t packetCount = 0;
static uint32_t lastTxMs   = 0;
static bool     loraReady  = false;
static bool     gpsFixSeen = false;

void setup() {
    Serial.begin(115200);
    delay(400);
    Serial.println("\n=== GPS Tracker LoRa — modular ===");

    buzzerInit();
    beepBoot();

    gpsInit();

    loraReady = loraInit();
    if (loraReady) beepLoraOK();
    else           beepLoraError();
}

void loop() {
    // 1. Alimenta o parser GPS com bytes da UART
    gpsProcess();

    // 2. Detecta primeiro fix
    if (!gpsFixSeen && gpsHasFix()) {
        gpsFixSeen = true;
        Serial.println("[GPS] Fix obtido!");
        beepGpsFix();
    }

    // 3. Transmissão periódica
    if (loraReady && (millis() - lastTxMs >= TX_INTERVAL_MS)) {
        lastTxMs = millis();
        packetCount++;

        GpsData data    = gpsGetData();
        String  payload = buildPayload(packetCount, data);

        if (loraSend(payload)) {
            beepTx();
        }
    }
}
