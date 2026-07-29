#include <Arduino.h>
#include "LittleFS.h"
#include "config.h"
#include "GpsModule.h"
#include "LoraReceiver.h"
#include "payload.h"

static bool loraReady = false;

// ── Contagem de pacotes perdidos e estatisticas ──
static uint32_t lastCount       = 0;    // ultimo count recebido do satellite
static uint32_t totalReceived   = 0;    // total de pacotes recebidos com sucesso
static uint32_t totalLost       = 0;    // total de pacotes perdidos (saltos no count)
static uint32_t totalErrors     = 0;    // total de pacotes com parse falho
static bool     firstPacket     = true; // true ate receber o primeiro pacote

// ── LittleFS ────────────────────────────────────
static String logPath;
static bool   fsReady = false;

/**
 * @brief Faz parse do CSV de 22 campos recebido do satellite.
 *
 * Formato v2.0 (alinhado com firmware do flight-computer, Fase 10):
 * TEAM_ID,millis,count,altp,temp,umi,p,gx,gy,gz,ax,ay,az,vz,
 * maxAltitude,state,alt,lat,lon,sat,parachute,rssi
 *
 * O campo "rssi" enviado pelo satellite e' placeholder (0); o RSSI real do
 * link descendente e' medido aqui (rxRssi) e usado no protocolPacket.
 *
 * Retorna true se o parse foi bem sucedido.
 */
static bool parseSatellitePacket(
    const String &raw,
    String &team_id,
    uint32_t &millis_ts,
    uint32_t &count,
    float &ax, float &ay, float &az,
    float &gx, float &gy, float &gz,
    float &temp, float &press, float &hum,
    float &altp,
    float &vz,
    float &max_alt,
    int   &state,
    float &lat, float &lon, float &alt,
    uint8_t &sats,
    int   &parachute,
    int   &rssi_placeholder
) {
    // --- End-of-packet marker validation ---
    // Satellite terminates every packet with '#' so the receiver can detect
    // truncation or corruption. If no '#', discard.
    if (!raw.endsWith("#")) {
        Serial.println("[PARSE] Missing end-of-packet marker (#) — discarded");
        return false;
    }
    // Strip the '#' before parsing
    String line = raw.substring(0, raw.length() - 1);

    // Valida numero de campos (22 campos = 21 virgulas)
    int commaCount = 0;
    for (unsigned i = 0; i < line.length(); i++) {
        if (line[i] == ',') commaCount++;
    }
    if (commaCount < 21) {
        Serial.println("[PARSE] Pacote incompleto: " + String(commaCount + 1) + " campos");
        return false;
    }

    int start = 0;

    auto nextField = [&](String &out) {
        int next = line.indexOf(',', start);
        if (next == -1) {
            out = line.substring(start);
            start = line.length();
        } else {
            out = line.substring(start, next);
            start = next + 1;
        }
    };

    String field;

    nextField(team_id);                // 0  TEAM_ID
    nextField(field); millis_ts = field.toInt();   // 1  millis
    nextField(field); count = field.toInt();        // 2  count
    nextField(field); altp = field.toFloat();       // 3  altp
    nextField(field); temp = field.toFloat();       // 4  temp
    nextField(field); hum = field.toFloat();        // 5  umi (0 se sem sensor)
    nextField(field); press = field.toFloat();      // 6  p
    nextField(field); gx = field.toFloat();         // 7  gx
    nextField(field); gy = field.toFloat();         // 8  gy
    nextField(field); gz = field.toFloat();         // 9  gz
    nextField(field); ax = field.toFloat();         // 10 ax
    nextField(field); ay = field.toFloat();         // 11 ay
    nextField(field); az = field.toFloat();         // 12 az
    nextField(field); vz = field.toFloat();         // 13 vz
    nextField(field); max_alt = field.toFloat();    // 14 maxAltitude
    nextField(field); state = field.toInt();        // 15 state
    nextField(field); alt = field.toFloat();        // 16 alt (GPS)
    nextField(field); lat = field.toFloat();        // 17 lat
    nextField(field); lon = field.toFloat();        // 18 lon
    nextField(field); sats = (uint8_t)field.toInt(); // 19 sat
    nextField(field); parachute = field.toInt();    // 20 parachute (0/1)
    nextField(field); rssi_placeholder = field.toInt(); // 21 rssi (placeholder)

    return true;
}

/**
 * @brief Atualiza contadores de pacotes perdidos e loga na Serial.
 *
 * Compara o count recebido com o anterior para detectar saltos.
 * No primeiro pacote, apenas inicializa o contador.
 */
static void trackPacketCount(uint32_t currentCount) {
    totalReceived++;

    if (firstPacket) {
        lastCount = currentCount;
        firstPacket = false;
        Serial.println("[STATS] Primeiro pacote recebido — count=" + String(currentCount));
        return;
    }

    // Detecta salto no contador
    if (currentCount == lastCount + 1) {
        // Sem perda — silencioso para nao poluir a Serial
    } else if (currentCount > lastCount + 1) {
        uint32_t lost = currentCount - lastCount - 1;
        totalLost += lost;
        Serial.println("[LOST] " + String(lost) + " pacote(s) perdido(s) — count "
                       + String(lastCount) + " -> " + String(currentCount)
                       + " | total perdidos: " + String(totalLost));
    } else {
        // count voltou (overflow ou reboot do satellite)
        Serial.println("[STATS] Count resetado — " + String(lastCount)
                       + " -> " + String(currentCount)
                       + " (possivel reboot do satellite)");
    }

    lastCount = currentCount;
}

/**
 * @brief Loga estatisticas acumuladas na Serial.
 */
static void logStats() {
    Serial.println("[STATS] Recebidos: " + String(totalReceived)
                   + " | Perdidos: " + String(totalLost)
                   + " | Erros parse: " + String(totalErrors)
                   + " | Taxa perda: "
                   + String(totalReceived + totalLost > 0
                            ? (totalLost * 100) / (totalReceived + totalLost)
                            : 0)
                   + "%");
}

// ── LittleFS ────────────────────────────────────

static bool setupLittleFS() {
    if (!LittleFS.begin(true)) {
        Serial.println("[FS] Falha ao montar LittleFS");
        return false;
    }
    Serial.printf("[FS] LittleFS OK — %u bytes total\n", (unsigned)LittleFS.totalBytes());
    return true;
}

static String generateLogPath() {
    for (int i = 1; i <= 999; i++) {
        char path[32];
        snprintf(path, sizeof(path), "/recovery_%03d.csv", i);
        if (!LittleFS.exists(path)) return String(path);
    }
    return String("/overflow.csv");
}

static void writeHeader(const char* path) {
    File f = LittleFS.open(path, FILE_WRITE);
    if (!f) { Serial.println("[FS] Erro ao criar cabecalho"); return; }
    f.println("millis,TEAM_ID,millis_ts,count,altp,temp,umi,p,gx,gy,gz,ax,ay,az,vz,maxAltitude,state,hora,data,alt,lat,lon,sat,parachute,rssi");
    f.close();
}

static void appendLog(const String &line) {
    if (!fsReady) return;
    File f = LittleFS.open(logPath.c_str(), FILE_APPEND);
    if (!f) { Serial.println("[FS] Erro ao abrir para append"); return; }
    f.println(line);
    f.close();
}

void setup() {
    Serial.begin(SERIAL_BAUD);
    delay(400);
    Serial.println();
    Serial.println("=== Recovery System — LoRa Receiver ===");
    Serial.println();

    gpsInit();

    loraReady = loraInit();

    fsReady = setupLittleFS();
    if (fsReady) {
        logPath = generateLogPath();
        writeHeader(logPath.c_str());
        Serial.printf("[FS] Log gravando em: %s\n", logPath.c_str());
    }

    Serial.println();
    Serial.println("[SYS] Aguardando pacotes LoRa do satellite...");
    Serial.println();
}

void loop() {
    gpsProcess();

    if (!loraReady || !loraAvailable()) {
        delay(10);
        return;
    }

    String raw = loraReceive();
    if (raw.length() == 0) return;

    int rxRssi = loraLastRSSI();
    Serial.print("[LoRa] RX (RSSI=" + String(rxRssi) + "): ");
    Serial.println(raw);

    // Parse do CSV do satellite
    String team_id;
    uint32_t millis_ts, count;
    float ax, ay, az, gx, gy, gz;
    float temp, press, hum, altp;
    float vz, max_alt;
    int state;
    float lat, lon, alt;
    uint8_t sats;
    int parachute;
    int rssi_placeholder;

    if (!parseSatellitePacket(raw, team_id, millis_ts, count,
                              ax, ay, az, gx, gy, gz,
                              temp, press, hum, altp,
                              vz, max_alt, state,
                              lat, lon, alt, sats, parachute, rssi_placeholder)) {
        totalErrors++;
        Serial.println("[STATS] Erro de parse #" + String(totalErrors));
        logStats();
        return;
    }

    // Rastreia pacotes perdidos
    trackPacketCount(count);

    // Hora/data do GPS local do receiver
    GpsTimeData gpsTime = gpsGetTimeData();

    // Monta pacote no formato do protocolo (22 campos + hora/data do receiver)
    String protocolPacket = buildProtocolPacket(
        team_id, millis_ts, count,
        ax, ay, az, gx, gy, gz,
        temp, press, hum, altp,
        vz, max_alt, state,
        lat, lon, alt, sats,
        parachute,
        gpsTime.hhmmss,
        gpsTime.ddmmyyyy,
        rxRssi       // RSSI real medido pelo receiver
    );

    // Retransmite via Serial para o Recovery WebUI
    Serial.println(protocolPacket);

    // Salva no LittleFS com timestamp local
    String logLine = String(millis()) + "," + protocolPacket;
    appendLog(logLine);
}
