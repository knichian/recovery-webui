#include <Arduino.h>
#include "Buzzer.h"
#include "config.h"

void buzzerInit() {
    pinMode(BUZZER_PIN, OUTPUT);
    digitalWrite(BUZZER_PIN, LOW);
}

void beep(int freq, int durationMs, int times) {
    for (int i = 0; i < times; i++) {
        tone(BUZZER_PIN, freq, durationMs);
        delay(durationMs + 50);
    }
    noTone(BUZZER_PIN);
}

void beepBoot()      { beep(1000, 100, 2); }
void beepLoraOK()    { beep(2000, 300, 1); }
void beepLoraError() { beep(400,  600, 3); }
void beepGpsFix()    { beep(1500, 150, 3); }
void beepTx()        { beep(2500,  40, 1); }
