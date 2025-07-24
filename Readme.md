# V2C Cloud Integration para Home Assistant

Esta integración permite controlar tu cargador V2C Trydan a través de la API Cloud de V2C, resolviendo el problema de compatibilidad cuando OCPP está activado.

## Problema resuelto

Cuando activas OCPP en tu V2C Trydan (necesario para conectarte con proveedores como Octopus Energy), el acceso HTTP local se desactiva, rompiendo las integraciones locales existentes. Esta integración usa la API Cloud de V2C para mantener el control completo.

## Características

### Sensores disponibles
- **Energía de carga**: Energía consumida en la sesión actual (kWh)
- **Kilómetros de carga**: Kilómetros equivalentes cargados
- **Potencia de carga**: Potencia actual de carga (W)
- **Estado de carga**: Estado textual del cargador
- **Tiempo de carga**: Duración de la sesión actual
- **Potencia contratada**: Potencia contratada de la casa
- **Potencia fotovoltaica**: Generación solar (si está configurada)
- **Potencia de casa**: Consumo total de la casa
- **Intensidad**: Corriente de carga actual (A)
- **Intensidad máxima/mínima**: Límites de corriente
- **Estados de control**: Dinámico, pausado, bloqueado, timer, etc.

### Controles disponibles
- **Switches**: Activar/desactivar carga dinámica, pausar carga, bloquear cargador
- **Controles numéricos**: Ajustar intensidad, intensidad máxima/mínima, kilómetros a cargar
- **Botones**: Iniciar/parar carga manualmente

### Eventos
- `v2c_cloud.charging_complete`: Se activa cuando se completa la carga programada

## Instalación

### Método 1: HACS (Recomendado)
1. Abre HACS en Home Assistant
2. Ve a "Integraciones"
3. Haz clic en "Repositorios personalizados"
4. Añade la URL: `https://github.com/tu-usuario/v2c_cloud`
5. Selecciona "Integración" como categoría
6. Busca "V2C Cloud" e instala

### Método 2: Manual
1. Descarga los archivos de esta integración
2. Copia la carpeta `v2c_cloud` a `config/custom_components/`
3. Reinicia Home Assistant

## Configuración

### Paso 1: Obtener Token de API
1. Ve a [v2c.cloud](https://v2c.cloud)
2. Inicia sesión con tu cuenta
3. Ve a la sección "API"
4. Genera un nuevo token y cópialo

### Paso 2: Obtener Device ID
1. En v2c.cloud, ve a la sección de dispositivos
2. Selecciona tu Trydan
3. Copia el ID del dispositivo (normalmente visible en la URL o detalles del dispositivo)

### Paso 3: Configurar en Home Assistant
1. Ve a "Configuración" → "Integraciones"
2. Haz clic en "Añadir integración"
3. Busca "V2C Cloud"
4. Introduce tu Token de API y Device ID
5. Haz clic en "Enviar"

## Uso

### Automatización de ejemplo
```yaml
# Pausar carga cuando el precio de la luz es alto
automation:
  - alias: "Pausar carga V2C precio alto"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pvpc_price
        above: 0.25
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.v2c_paused

# Reanudar carga cuando el precio baja
  - alias: "Reanudar carga V2C precio bajo"
    trigger:
      - platform: numeric_state
        entity_id: sensor.pvpc_price
        below: 0.15
    action:
      - service: switch.turn_off
        target:
          entity_id: switch.v2c_paused
```

### Control de carga por exceso solar
```yaml
# Activar carga dinámica cuando hay exceso solar
automation:
  - alias: "Carga solar V2C"
    trigger:
      - platform: numeric_state
        entity_id: sensor.v2c_fv_power
        above: 2000
    condition:
      - condition: state
        entity_id: sensor.v2c_charge_state
        state: "Manguera conectada (NO CARGA)"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.v2c_dynamic
      - service: number.set_value
        target:
          entity_id: number.v2c_intensity
        data:
          value: 6
```

### Notificación de carga completa
```yaml
automation:
  - alias: "Notificar carga V2C completa"
    trigger:
      - platform: event
        event_type: v2c_cloud.charging_complete
    action:
      - service: notify.mobile_app_mi_telefono
        data:
          title: "Carga completa"
          message: "El vehículo ha alcanzado los kilómetros programados"
```

## Comparación con integración local

| Característica | Local HTTP | V2C Cloud |
|---------------|------------|-----------|
| Funciona con OCPP | ❌ No | ✅ Sí |
| Velocidad de respuesta | Muy rápida | Rápida |
| Dependencia internet | No | Sí |
| Funcionalidades | Completas | Completas |
| Configuración | IP local | Token + Device ID |

## Solución de problemas

### Error de conexión
- Verifica que el token sea válido y no haya expirado
- Confirma que el Device ID sea correcto
- Asegúrate de que tu V2C esté conectado a internet

### Token inválido
- Regenera el token en v2c.cloud
- Reconfigura la integración con el nuevo token

### Funcionalidades limitadas
- Algunas funcionalidades pueden variar según la versión de firmware del Trydan
- Consulta la documentación de V2C para funcionalidades específicas de tu modelo

## Contribuir

Si encuentras problemas o quieres añadir funcionalidades:
1. Abre un issue en GitHub
2. Envía un pull request con mejoras
3. Comparte feedback sobre la integración

## Licencia

Esta integración es software libre bajo licencia MIT.

## Agradecimientos

- Basado en el trabajo de [Rain1971](https://github.com/Rain1971/V2C_trydant) para la integración HTTP local
- Documentación de API de V2C en [v2c.docs.apiary.io](https://v2c.docs.apiary.io/)