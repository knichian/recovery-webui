#pragma once
#include <Arduino.h>

bool loraInit();                      // Retorna true se OK
bool loraSend(const String& payload); // Retorna true se enviou
int  loraLastRSSI();                  // RSSI do último pacote recebido
