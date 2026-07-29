#pragma once
#include <Arduino.h>

bool loraInit();                      // Inicializa LoRa (freq, sync word, etc.)
bool loraSend(const String& payload); // Envia pacote LoRa
int  loraLastRSSI();                  // RSSI do ultimo pacote recebido (para debug)
