#pragma once

void buzzerInit();

// Bip simples: frequência (Hz), duração (ms), repetições
void beep(int freq, int durationMs, int times = 1);

// Padrões semânticos prontos
void beepBoot();       // Dois bips curtos  — sistema ligando
void beepLoraOK();     // Um bip médio      — LoRa inicializado
void beepLoraError();  // Três bips longos  — falha no LoRa
void beepGpsFix();     // Três bips médios  — GPS com fix
void beepTx();         // Um bip curtíssimo — pacote enviado
//não tenho certeza da necessidade de todos esses bips mas me fala oq achar
