#pragma once

#include <Arduino.h>

struct BeaconData {
    uint32_t millis;
    uint32_t count;

    float altp;
    float temp;
    float umi;
    float p;
    float gp;
    float gr;
    float gy;
    float ap;
    float ar;
    float ay;

    float alt;
    float lat;
    float lon;
    uint8_t sat;
    uint8_t pqd;
};

static String buildBeaconPacket(
    const String &team_id,
    const BeaconData &d
) {
    char buffer[200];
    snprintf(buffer, sizeof(buffer),
        "%s,%lu,%lu,"
        "%.2f,%.2f,%.2f,%.2f,"
        "%.2f,%.2f,%.2f,"
        "%.2f,%.2f,%.2f,"
        "%.2f,%.6f,%.6f,"
        "%u,%u,%d",
        team_id.c_str(),
        d.millis, d.count,
        d.altp, d.temp, d.umi, d.p,
        d.gp, d.gr, d.gy,
        d.ap, d.ar, d.ay,
        d.alt, d.lat, d.lon,
        d.sat, d.pqd, -1
    );
    return String(buffer);
}
