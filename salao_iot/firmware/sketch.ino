/*
  Console da Cadeira (ESP32 no Wokwi) - Salão IoT
  Botões: Café, Água, Sujeira (atalho), Limpeza (iniciar/concluir), Copa (pedido entregue)
  LEDs:   verde = zona liberada | vermelho fixo = suja | vermelho piscando = em limpeza
  Buzzer: toca quando chega um novo pedido na copa
*/
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <HTTPClient.h>
#include <ArduinoJson.h>

// ====== CONFIGURE AQUI ======
const char* WIFI_SSID = "Wokwi-GUEST";
const char* WIFI_PASS = "";
const char* API_URL   = "https://SEU-TUNEL.ngrok-free.app";  // sem barra no final
const int   CADEIRA   = 1;
const char* FUNCIONARIO = "copa-01";
// ============================

const int PIN_CAFE = 12, PIN_AGUA = 13, PIN_SUJA = 14, PIN_LIMPEZA = 15, PIN_COPA = 4;
const int LED_VERDE = 26, LED_VERMELHO = 27, BUZZER = 33;

struct Botao { int pino; bool ultimo; unsigned long t; };
Botao botoes[5] = {
  {PIN_CAFE, HIGH, 0}, {PIN_AGUA, HIGH, 0}, {PIN_SUJA, HIGH, 0},
  {PIN_LIMPEZA, HIGH, 0}, {PIN_COPA, HIGH, 0}
};

WiFiClientSecure clienteSeguro;
WiFiClient clientePlano;

String estado = "pronta";
int pendentesAnterior = 0;
unsigned long ultimoPolling = 0, ultimoPisca = 0;
bool piscaLigado = false;

bool chamarApi(const String& metodo, const String& caminho, const String& corpo, String* resposta = nullptr) {
  String url = String(API_URL) + caminho;
  HTTPClient http;
  bool https = url.startsWith("https");
  bool ok = https ? http.begin(clienteSeguro, url) : http.begin(clientePlano, url);
  if (!ok) return false;
  http.addHeader("Content-Type", "application/json");
  http.addHeader("ngrok-skip-browser-warning", "true");
  int codigo = (metodo == "GET") ? http.GET() : http.POST(corpo);
  if (resposta && codigo > 0) *resposta = http.getString();
  Serial.printf("%s %s -> %d\n", metodo.c_str(), caminho.c_str(), codigo);
  http.end();
  return codigo >= 200 && codigo < 300;
}

String corpoFuncionario() {
  return String("{\"funcionario\":\"") + FUNCIONARIO + "\"}";
}

bool apertou(Botao& b) {
  bool leitura = digitalRead(b.pino);
  bool evento = false;
  if (leitura != b.ultimo && millis() - b.t > 50) {   // debounce
    b.t = millis();
    if (leitura == LOW) evento = true;                // borda de descida
    b.ultimo = leitura;
  }
  return evento;
}

void atualizarLeds() {
  if (estado == "suja") {
    digitalWrite(LED_VERMELHO, HIGH); digitalWrite(LED_VERDE, LOW);
  } else if (estado == "em_limpeza") {
    if (millis() - ultimoPisca > 400) { ultimoPisca = millis(); piscaLigado = !piscaLigado; }
    digitalWrite(LED_VERMELHO, piscaLigado); digitalWrite(LED_VERDE, LOW);
  } else {
    digitalWrite(LED_VERMELHO, LOW); digitalWrite(LED_VERDE, HIGH);
  }
}

void consultarConsole() {
  String resp;
  if (!chamarApi("GET", "/console/" + String(CADEIRA), "", &resp)) return;
  JsonDocument doc;
  if (deserializeJson(doc, resp)) return;
  estado = doc["estado"].as<String>();
  int pendentes = doc["pedidos_pendentes"] | 0;
  if (pendentes > pendentesAnterior) tone(BUZZER, 1000, 300);  // novo pedido na copa
  pendentesAnterior = pendentes;
  Serial.printf("estado=%s pendentes=%d\n", estado.c_str(), pendentes);
}

void setup() {
  Serial.begin(115200);
  for (auto& b : botoes) pinMode(b.pino, INPUT_PULLUP);
  pinMode(LED_VERDE, OUTPUT); pinMode(LED_VERMELHO, OUTPUT); pinMode(BUZZER, OUTPUT);
  clienteSeguro.setInsecure();   // aceita o certificado do túnel (apenas para simulação)

  WiFi.begin(WIFI_SSID, WIFI_PASS, 6);
  Serial.print("Conectando ao Wi-Fi");
  while (WiFi.status() != WL_CONNECTED) { delay(300); Serial.print("."); }
  Serial.println(" conectado!");
}

void loop() {
  if (apertou(botoes[0])) chamarApi("POST", "/pedidos", "{\"cadeira\":" + String(CADEIRA) + ",\"tipo\":\"cafe\"}");
  if (apertou(botoes[1])) chamarApi("POST", "/pedidos", "{\"cadeira\":" + String(CADEIRA) + ",\"tipo\":\"agua\"}");
  if (apertou(botoes[2])) chamarApi("POST", "/zonas/" + String(CADEIRA) + "/suja", "{}");
  if (apertou(botoes[3])) {   // alterna conforme o estado da zona
    if (estado == "suja")
      chamarApi("POST", "/zonas/" + String(CADEIRA) + "/limpeza/iniciar", corpoFuncionario());
    else if (estado == "em_limpeza")
      chamarApi("POST", "/zonas/" + String(CADEIRA) + "/limpeza/concluir", corpoFuncionario());
  }
  if (apertou(botoes[4])) chamarApi("POST", "/pedidos/concluir-proximo", corpoFuncionario());

  if (millis() - ultimoPolling > 2000) { ultimoPolling = millis(); consultarConsole(); }
  atualizarLeds();
}
