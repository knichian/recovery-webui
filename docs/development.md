# Guia de Desenvolvimento

Este guia fornece informações para desenvolvedores que desejam contribuir ou modificar o Recovery WebUI.

## Índice

- [Configuração do Ambiente](#configuração-do-ambiente)
- [Estrutura do Código](#estrutura-do-código)
- [Padrões de Código](#padrões-de-código)
- [Testando Mudanças](#testando-mudanças)
- [Adicionando Funcionalidades](#adicionando-funcionalidades)
- [Debugging](#debugging)
- [Contribuindo](#contribuindo)

## Configuração do Ambiente

### 1. Ferramentas Necessárias

```bash
# Git
sudo apt install git  # Ubuntu/Debian
brew install git      # macOS

# Python 3.7+
python3 --version

# pip
python3 -m pip --version

# Editor (recomendados)
# - VS Code com extensões Python
# - PyCharm
# - Vim/Neovim com plugins Python
```

### 2. Clone e Setup

```bash
# Clone o repositório
git clone <url-do-repositorio>
cd recovery-webui

# Crie um ambiente virtual
python3 -m venv venv
source venv/bin/activate  # Linux/macOS
# ou
venv\Scripts\activate  # Windows

# Instale dependências de desenvolvimento
pip install -r requirements.txt
pip install black flake8 pytest pylint  # Ferramentas de dev (opcional)
```

### 3. Ferramentas de Desenvolvimento (Opcional)

```bash
# Black - Formatador de código
pip install black

# Flake8 - Linter
pip install flake8

# Pylint - Análise estática
pip install pylint

# Pytest - Framework de testes
pip install pytest

# IPython - Shell interativo melhorado
pip install ipython
```

## Estrutura do Código

### Backend (Python)

```
src/
├── app.py                  # Aplicação Flask principal
│   ├── Flask app initialization
│   ├── Routes (/, /satellite)
│   ├── SocketIO event handlers
│   └── background_thread()
│
├── modules/
│   ├── __init__.py        # Importações do módulo
│   └── SerialCOM.py       # Comunicação serial
│       ├── class base_com
│       └── def list_ports()
│
web/
├── templates/             # Templates Jinja2
│   ├── base.html         # Template base
│   ├── index.html        # Página do foguete
│   └── satellite.html    # Página do satélite
│
├── static/               # Arquivos estáticos
│   ├── css/
│   │   └── app.css      # Estilos customizados
│   ├── js/
│   │   └── app.js       # Lógica do cliente
│   └── logs/
│       └── log.csv      # Logs de telemetria
```

### Frontend (JavaScript)

```
static/js/app.js
├── Inicialização do mapa (Leaflet)
├── Configuração Socket.IO
├── Event handlers
│   ├── updateRocket
│   └── updateSat
└── Funções de atualização
    ├── addData()
    ├── addSatData()
    ├── MapPoint()
    └── MapSatPoint()
```

## Padrões de Código

### Python (Backend)

#### Estilo de Código

Seguimos as convenções [PEP 8](https://pep8.org/):

```python
# Bom ✓
def calculate_altitude(pressure, temperature):
    """Calcula altitude baseada em pressão e temperatura."""
    altitude = (pressure - 1013.25) * 8.5
    return altitude

# Ruim ✗
def calcAlt(p,t):
    return (p-1013.25)*8.5
```

#### Formatação com Black

```bash
# Formatar todos os arquivos Python
black src/

# Verificar sem modificar
black --check src/

# Formatar arquivo específico
black src/app.py
```

#### Linting com Flake8

```bash
# Verificar todos os arquivos
flake8 src/

# Ignorar certos erros (opcional)
flake8 --ignore=E501,W503 src/
```

### JavaScript (Frontend)

#### Estilo de Código

```javascript
// Bom ✓
function addDataToMap(latitude, longitude, timestamp) {
  const marker = L.marker([latitude, longitude]);
  marker.bindPopup(`Position at ${timestamp}`);
  layerGroup.addLayer(marker);
}

// Ruim ✗
function add(lat, lon, t) {
  var m = L.marker([lat, lon]);
  m.bindPopup("Position at " + t);
  layerGroup.addLayer(m);
}
```

#### Convenções

- Use `const` e `let` em vez de `var`
- Use template strings para concatenação
- Adicione comentários para lógica complexa
- Mantenha funções pequenas e focadas

### HTML/CSS

```html
<!-- Bom ✓ -->
<div class="data-container">
  <h2 class="section-title">Dados do Foguete</h2>
  <table class="data-table">
    <!-- conteúdo -->
  </table>
</div>

<!-- Ruim ✗ -->
<div class="dc">
  <h2>Dados do Foguete</h2>
  <table>
    <!-- conteúdo -->
  </table>
</div>
```

## Testando Mudanças

### Teste Manual Básico

1. **Teste sem hardware real:**

```python
# Crie um arquivo test_mock.py
import time
from module import base_com

class MockSerial:
    """Mock da porta serial para testes."""

    def __init__(self):
        self.is_open = True
        self.counter = 0

    def readline(self):
        self.counter += 1
        # Simula dados do foguete
        data = f"#100,{self.counter*1000},{ self.counter},150.5,25.3,45.2,1013.25,0.5,1.2,-0.3,0.1,0.2,9.8,143045,20250120,150.0,-23.5505,-46.6333,8,0,-75\n"
        time.sleep(0.5)
        return data.encode('utf-8')

    def close(self):
        pass

# Use no app.py durante desenvolvimento
# com = MockSerial()
```

2. **Teste de integração:**

```bash
# Terminal 1: Execute o servidor
cd app
python3 app.py

# Terminal 2: Teste com curl
curl http://localhost:5000/

# Terminal 3: Teste WebSocket com Python
python3 test_websocket_client.py
```

### Testes Automatizados

#### Estrutura de Testes

```
recovery-webui/
└── tests/
    ├── __init__.py
    ├── test_serial.py       # Testes SerialCOM
    ├── test_app.py          # Testes Flask app
    └── test_websocket.py    # Testes WebSocket
```

#### Exemplo de Teste (PyTest)

```python
# tests/test_serial.py
import pytest
from module.SerialCOM import list_ports

def test_list_ports():
    """Testa listagem de portas."""
    ports = list_ports()
    assert isinstance(ports, list)

def test_base_com_init():
    """Testa inicialização da classe base_com."""
    # Teste com mock ou hardware real
    pass
```

#### Executar Testes

```bash
# Instale pytest
pip install pytest

# Execute todos os testes
pytest

# Execute com verbosidade
pytest -v

# Execute teste específico
pytest tests/test_serial.py

# Execute com cobertura
pip install pytest-cov
pytest --cov=app tests/
```

## Adicionando Funcionalidades

### 1. Adicionar Novo Campo de Telemetria

**Exemplo:** Adicionar campo de velocidade vertical

**Backend (app.py):**

```python
def background_thread():
    # ... código existente ...

    # Adicione o novo campo no parse
    TEAM_ID,millis,count,altp,temp,umi,p,gp,gr,gy,ap,ar,ay,hora,data,alt,lat,lon,sat,pqd,rssi,vvel = fields

    if TEAM_ID == '#100':
        socketio.emit('updateRocket', {
            'latitude': lat,
            'longitude': lon,
            'altura': altp,
            'satelites': sat,
            'rssi': rssi,
            'pqd': pqd,
            'velocidadeVertical': vvel,  # Novo campo
            'time': now
        })
```

**Frontend (app.js):**

```javascript
socket.on("updateRocket", function (msg) {
  var jsonData = msg;
  var latitude = jsonData.latitude;
  var longitude = jsonData.longitude;
  var satelites = jsonData.satelites;
  var time = jsonData.time;
  var altura = jsonData.altura;
  var rssi = jsonData.rssi;
  var pqd = jsonData.pqd;
  var vvel = jsonData.velocidadeVertical; // Novo campo

  addData(latitude, longitude, altura, satelites, time, rssi, pqd, vvel);
});
```

**Template (index.html):**

```html
<table>
  <tr>
    <th>Horário</th>
    <th>Latitude</th>
    <th>Longitude</th>
    <th>Altura</th>
    <th>Satélites</th>
    <th>RSSI</th>
    <th>Paraquedas</th>
    <th>Vel. Vertical</th>
    <!-- Nova coluna -->
  </tr>
</table>
```

### 2. Adicionar Nova Página

**Criar template (templates/analysis.html):**

```html
{% extends "base.html" %} {% block content %}
<main>
  <div class="card">
    <h1>Análise de Dados</h1>
    <!-- Conteúdo da página -->
  </div>
</main>
{% endblock %}
```

**Adicionar route (app.py):**

```python
@app.route('/analysis')
def analysis():
    return render_template('analysis.html')
```

**Adicionar link na navegação (base.html):**

```html
<nav>
  <a href="/">Foguete</a>
  <a href="/satellite">Satélite</a>
  <a href="/analysis">Análise</a>
  <!-- Novo link -->
</nav>
```

### 3. Adicionar API REST Endpoint

**Exemplo:** Endpoint para consultar histórico

```python
from flask import jsonify

@app.route('/api/history')
def get_history():
    """Retorna histórico de dados do log."""
    try:
        with open('web/static/logs/log.csv', 'r') as f:
            lines = f.readlines()[1:]  # Pula header
            data = [line.strip().split(',') for line in lines]
        return jsonify({'success': True, 'data': data})
    except FileNotFoundError:
        return jsonify({'success': False, 'error': 'Log não encontrado'}), 404

@app.route('/api/stats')
def get_stats():
    """Retorna estatísticas do voo."""
    # Implementar cálculo de estatísticas
    stats = {
        'max_altitude': 0,
        'max_speed': 0,
        'flight_time': 0
    }
    return jsonify(stats)
```

## Debugging

### Backend (Python)

#### Prints de Debug

```python
def background_thread():
    print("Thread started")  # Debug
    while True:
        try:
            response = com.read_response()
            print(f"Raw data: {response}")  # Debug

            if not response:
                print("Empty response")  # Debug
                socketio.sleep(0.5)
                continue

            # ... resto do código ...
        except Exception as e:
            print(f"Error: {e}")  # Debug
            import traceback
            traceback.print_exc()  # Stack trace completo
```

#### Debugger Interativo (pdb)

```python
def background_thread():
    while True:
        try:
            response = com.read_response()

            # Breakpoint - execução para aqui
            import pdb; pdb.set_trace()

            # Agora você pode inspecionar variáveis
            # Digite 'n' para próxima linha
            # Digite 'c' para continuar
            # Digite 'p variavel' para imprimir

            fields = response.split(',')
            # ...
```

#### Logging Estruturado

```python
import logging

# Configurar logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def background_thread():
    logger.info("Background thread started")
    while True:
        try:
            response = com.read_response()
            logger.debug(f"Received: {response}")
            # ...
        except Exception as e:
            logger.error(f"Error in background thread: {e}", exc_info=True)
```

### Frontend (JavaScript)

#### Console do Navegador

```javascript
// Adicione console.logs estratégicos
socket.on("updateRocket", function (msg) {
  console.log("Raw message:", msg);
  console.log("Parsed data:", {
    lat: msg.latitude,
    lon: msg.longitude,
    alt: msg.altura,
  });

  // Verifique se valores são válidos
  if (!msg.latitude || !msg.longitude) {
    console.error("Invalid coordinates!", msg);
    return;
  }

  addData(/* ... */);
});
```

#### Debugger do Navegador

```javascript
function addData(latitude, longitude, altura, satelites, time, rssi, pqd) {
  // Breakpoint - adicione via DevTools ou:
  debugger;

  // Execução para aqui, você pode inspecionar variáveis
  addFirstPoint(latitude, longitude);
  MapPoint(latitude, longitude, time);
  // ...
}
```

### Ferramentas Úteis

#### Monitor de WebSocket

Use a aba "Network" → "WS" no Chrome DevTools para ver mensagens WebSocket em tempo real.

#### Monitor Serial (alternativa)

```bash
# Linux/macOS
screen /dev/ttyACM0 115200

# ou
minicom -D /dev/ttyACM0 -b 115200

# Windows
# Use PuTTY ou Arduino IDE Serial Monitor
```

## Contribuindo

### Workflow de Contribuição

1. **Fork o repositório**
2. **Crie uma branch para sua feature:**
   ```bash
   git checkout -b feature/minha-feature
   ```
3. **Faça commits atômicos:**
   ```bash
   git commit -m "Adiciona campo de velocidade vertical"
   ```
4. **Push para seu fork:**
   ```bash
   git push origin feature/minha-feature
   ```
5. **Abra um Pull Request**

### Convenções de Commit

Use mensagens descritivas:

```bash
# Bom ✓
git commit -m "Adiciona validação de coordenadas GPS"
git commit -m "Corrige erro de parse CSV quando dados incompletos"
git commit -m "Melhora performance do render do mapa"

# Ruim ✗
git commit -m "fix"
git commit -m "changes"
git commit -m "update"
```

### Checklist antes do PR

- [ ] Código segue os padrões estabelecidos
- [ ] Código foi testado manualmente
- [ ] Adicionados comentários em lógica complexa
- [ ] Documentação atualizada (se necessário)
- [ ] Sem console.logs desnecessários
- [ ] Sem credenciais ou dados sensíveis

### Code Review

Ao revisar PRs, verifique:

- Funcionalidade implementada corretamente
- Código legível e manutenível
- Performance adequada
- Tratamento de erros
- Compatibilidade com código existente

## Recursos Adicionais

### Documentação de Dependências

- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask-SocketIO](https://flask-socketio.readthedocs.io/)
- [PySerial](https://pyserial.readthedocs.io/)
- [Leaflet.js](https://leafletjs.com/reference.html)
- [Socket.IO Client](https://socket.io/docs/v4/client-api/)

### Tutoriais Úteis

- [Real Python - Flask Tutorial](https://realpython.com/tutorials/flask/)
- [Socket.IO Tutorial](https://socket.io/get-started/chat)
- [Leaflet Quick Start](https://leafletjs.com/examples/quick-start/)

### Comunidade

- Abra issues para reportar bugs
- Use discussions para perguntas
- Contribua com documentação

## Troubleshooting Desenvolvimento

### Mudanças não aparecem

**Problema:** Alterações no código não refletem no navegador

**Soluções:**

```bash
# 1. Limpe cache do navegador (Ctrl+Shift+Delete)
# 2. Hard reload (Ctrl+Shift+R)
# 3. Reinicie o servidor Flask
# 4. Verifique se está editando o arquivo correto
```

### Erro de import

**Problema:** `ModuleNotFoundError: No module named 'X'`

**Solução:**

```bash
# Verifique se está no ambiente virtual
which python  # Deve apontar para venv/bin/python

# Reinstale dependências
pip install -r requirements.txt

# Ou instale módulo específico
pip install nome-do-modulo
```

### Hot reload não funciona

**Problema:** Servidor não reinicia automaticamente

**Solução:**

```python
# Use debug mode (apenas desenvolvimento!)
if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
```

⚠️ **Nunca use `debug=True` em produção!**

---

## Próximos Passos

Agora que você está configurado:

1. Explore o código existente
2. Tente adicionar uma pequena feature
3. Leia a [Arquitetura do Sistema](architecture.md) para entender melhor o design
4. Consulte a [Documentação da API](api.md) para integração

**Boa sorte com o desenvolvimento! 🚀**

---

[← Voltar ao README](../README.md)
