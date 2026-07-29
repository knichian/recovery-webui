#pragma once


// ── LoRa RFM95W (SPI) ──────────────────────────
#define LORA_SCK        4
#define LORA_MOSI       3
#define LORA_MISO       2
#define LORA_CS         5
#define LORA_RST        6
#define LORA_IRQ        7

#define LORA_FREQUENCY  868E6   // Hz  (868 BR/EU | 915 EUA)
#define LORA_SF         7       // Spreading Factor 7–12
#define LORA_BW         125E3   // Bandwidth Hz
#define LORA_CR         5       // Coding Rate (4/5)
#define LORA_TX_POWER   17      // dBm

// ── GPS (UART1) ─────────────────────────────────
#define GPS_RX_PIN      20
#define GPS_TX_PIN      21
#define GPS_BAUD        9600

// ── Buzzer ──────────────────────────────────────
#define BUZZER_PIN      11

// ── Lógica de aplicação ─────────────────────────
#define TX_INTERVAL_MS  10000   // Intervalo entre pacotes LoRa (ms)
