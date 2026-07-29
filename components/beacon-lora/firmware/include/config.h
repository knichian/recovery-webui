#pragma once

// ── LoRa RFM95W (SPI) ──────────────────────────
// Mesmos pinos do receiver
#define LORA_SCK        4
#define LORA_MOSI       3
#define LORA_MISO       2
#define LORA_CS         5
#define LORA_RST        6
#define LORA_IRQ        7

#define LORA_FREQUENCY  915E6   // Hz (915 MHz Americas/Brasil)
#define LORA_SYNC_WORD  0xF3    // deve bater com receiver
#define LORA_SF         7       // Spreading Factor 7–12
#define LORA_BW         125E3   // Bandwidth Hz
#define LORA_CR         5       // Coding Rate (4/5)
#define LORA_TX_POWER   17      // dBm

// ── GPS (UART1) ─────────────────────────────────
#define GPS_RX_PIN      20
#define GPS_TX_PIN      21
#define GPS_BAUD        9600

// ── Serial (USB) ────────────────────────────────
#define SERIAL_BAUD     115200

// ── Configurações de transmissão ────────────────
#define TX_INTERVAL_MS  200     // 5 Hz
#define TEAM_ID         "#213"
