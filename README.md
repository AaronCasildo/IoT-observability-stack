# Monitoreo IoT con InfluxDB, Prometheus y Grafana  

Este repositorio documenta el despliegue de un stack completo de monitoreo para un caso de uso de **Internet de las Cosas (IoT)**.  
El proyecto integra:  

- **InfluxDB** → para datos de series temporales.  
- **Prometheus** → para métricas de infraestructura.  
- **Grafana** → para la visualización unificada.  

Todo se despliega en una instancia de **Amazon EC2**, asegurada mediante una **VPN con Tailscale**.  

---

## Arquitectura de la Solución  

La arquitectura implementada consiste en un servidor central en EC2 que aloja todo el stack de observabilidad.  

- Los datos simulados de sensores IoT se inyectan en **InfluxDB**.  
- **Prometheus** recolecta métricas del estado del servidor vía **Node Exporter**.  
- **Grafana** se conecta a ambas fuentes para centralizar la visualización en un dashboard único y seguro.  
- El acceso se restringe mediante la red privada de **Tailscale**, evitando exponer puertos públicos.  

---

## Estructura del Repositorio  

La documentación se organiza en carpetas para facilitar la lectura y seguimiento de cada etapa:  

---

## Desarrollo  

### 1. Configuración de Tailscale  
Se configuró una **VPN con Tailscale** para interconectar de forma segura la instancia EC2 y los dispositivos personales.  
Esto eliminó la necesidad de exponer puertos públicos, aumentando la seguridad.  
<img width="882" height="494" alt="image" src="https://github.com/user-attachments/assets/ff5ec348-cdf8-4538-b832-cfe797ad3a73" />

---

### 2. Instalación de InfluxDB  
- Instalación desde repositorio oficial.  
- Creación de **organización**, **bucket** y **token** de autenticación.  

[Ver Pasos de Instalación de InfluxDB](./InfluxDB/readme.md)  

---

### 3. Instalación de Prometheus + Node Exporter  
- Servicios configurados con **systemd**.  
- Archivo `prometheus.yml` actualizado para monitoreo de endpoints.  

[Ver Pasos de Instalación de Prometheus](./Prometheus/readme.md)  

---

### 4. Instalación de Grafana  
- Instalación y habilitación del servicio.  
- Configuración de **data sources**: InfluxDB y Prometheus.  

[Ver Pasos de Instalación de Grafana](./Grafana/readme.md)  

---

### 5. Simulación de Datos IoT  
Se desarrolló un script en **Python** que simula un sensor de **temperatura y humedad**, enviando datos a InfluxDB cada segundo.  
```python
from datetime import datetime
import random
import time
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS

# --- CONFIGURACIÓN ---
token = "###########################################################################################"
org = "SistemasProgramables"
bucket = "datos"

# Inicializar cliente InfluxDB
client = InfluxDBClient(url="http://localhost:8086", token=token, org=org)
write_api = client.write_api(write_options=SYNCHRONOUS)

print("--- Simulador IoT iniciado ---")

try:
    while True:
        temperatura = round(random.uniform(18.0, 30.0), 2)
        humedad = round(random.uniform(40.0, 70.0), 2)

        punto = (
            Point("ambiente")
            .tag("ubicacion", "laboratorio")
            .field("temperatura", temperatura)
            .field("humedad", humedad)
            .time(datetime.utcnow(), WritePrecision.NS)
        )

        write_api.write(bucket=bucket, record=punto)
        print(f"Enviado: temperatura={temperatura}°C, humedad={humedad}%")
        time.sleep(1)

except KeyboardInterrupt:
    print("\n--- Simulador detenido ---")
except Exception as e:
    print(f"Error: {e}")
```

### 6. Dashboard en Grafana  
Se creó un dashboard unificado que integra:  

- **Métricas IoT** desde InfluxDB.  
- **Métricas de sistema** desde Prometheus/Node Exporter.  

<img width="1920" height="766" alt="image" src="https://github.com/user-attachments/assets/3f552448-1152-4e5e-ab8f-b9ed93469339" />

Demo disponible en:  
https://www.loom.com/share/f94ea96f614f4f27ba8b4551e6919132?sid=2fa52b00-1ebd-4673-b69a-e5b9d80e9078

---

### 7. Notas y Reflexiones  

**Importancia de Tailscale en este escenario:**  
Tailscale permite crear una VPN de malla entre dispositivos y el servidor EC2, evitando exponer puertos públicos como **3000 (Grafana)** o **9090 (Prometheus)**.  
Esto reduce la superficie de ataque y garantiza acceso seguro solo a dispositivos autorizados en la Tailnet.  

**Diferencia entre métricas de IoT e infraestructura:**  

- **Métricas IoT (InfluxDB):** datos de sensores (ej. temperatura, humedad). Indican *qué* ocurre en el proceso o ambiente.  
- **Métricas de sistema (Prometheus/Node Exporter):** datos del servidor (CPU, memoria, red). Indican *cómo* funciona la infraestructura que soporta la aplicación.  

---

## Autor  

**Aaron Casildo Rubalcava**
