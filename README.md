# Criminopatía
Scrapea y descarga todos los episodios de [Criminopatía](https://criminopatia.com/) (pensado para importarlos en un media system como Jellyfin).

![Criminopatía](https://github.com/ifayost/Criminopatia/blob/main/Cabeceras-Criminopatia-Tw-02.png?raw=true)

Criminopatía es un podcast de crímenes reales dirigido por Clara Tiscar, para mí el mejor podcast de True Crime de habla hispana. Si dispones cuenta para acceder al club de fans o al archivo también puedes descargar todos estos episodios. Si eres fan de los podcasts de True Crime merece totalmente la pena la suscripción.

usage: criminopatia [-h] [--episodes] [--cf] [--archivo]

    Scrapea y descarga todos los episodios de Criminopatía.

    options:
      -h, --help  show this help message and exit
      --episodes  Scrapea y descarga los episodios
      --cf        Scrapea y descarga el contenido del club de fans
      --archivo   Scrapea y descarga el contenido de los archivos

    Si no se añade ninguna flag, por defecto scrapea y descarga los episodios y el club de fans.

## Instalación con Docker (Recomendado)

La forma más sencilla de usar esta herramienta es mediante Docker, ya que evita conflictos de dependencias y configuración.

### Construir la imagen
```bash
docker build -t criminopatia .
```

### Variables de entorno opcionales
| Variable | Valores | Descripción |
|----------|---------|-------------|
| `RUN_EPISODES` | `true`/`false` | Descargar episodios regulares |
| `RUN_CF` | `true`/`false` | Descargar club de fans (requiere login) |
| `RUN_ARCHIVO` | `true`/`false` | Descargar contenido archivado (requiere login) |

### Ejemplos de uso

Mostrar ayuda:
```bash
docker run --rm criminopatia
```

Descargar solo episodios:
```bash
docker run --rm -e RUN_EPISODES=true \
  -v $(pwd)/Criminopatia:/Criminopatia criminopatia
```

Descargar club de fans (requiere cuenta):
```bash
docker run --rm -e RUN_CF=true \
  -e CRIMINOPATIA_USER=usuario \
  -e CRIMINOPATIA_PASSWORD=contraseña \
  -v $(pwd)/Criminopatia:/Criminopatia criminopatia
```

Descargar todo (episodios + club de fans):
```bash
docker run --rm -e RUN_EPISODES=true -e RUN_CF=true \
  -e CRIMINOPATIA_USER=usuario \
  -e CRIMINOPATIA_PASSWORD=contraseña \
  -v $(pwd)/Criminopatia:/Criminopatia criminopatia
```

## Automatización con Podman Quadlet

Para automatizar las descargas cada jueves a las 08:00, puedes usar Podman con systemd Quadlets. Esto permite ejecutar el contenedor programado sin necesidad de root y con gestión de secretos integrada.

### Requisitos previos

1. **Instalar Podman** en tu distribución
2. **Habilitar user-level systemd**:
   ```bash
   systemctl --user enable --now podman.socket
   ```

### Construir la imagen

```bash
podman build -t criminopatia .
```

### Autenticación

#### Opción A: Podman secrets (Recomendado)

Guarda tus credenciales de forma segura en el almacén de secretos de Podman:

```bash
echo -n "tu_usuario" | podman secret create CRIMINOPATIA_USER -
echo -n "tu_contraseña" | podman secret create CRIMINOPATIA_PASSWORD -
```

#### Opción B: Archivo .env (Más sencillo)

Crea un archivo con tus credenciales:

```bash
# ~/.config/containers/systemd/criminopatia.env
RUN_EPISODES=true
RUN_CF=true
CRIMINOPATIA_USER=tu_usuario
CRIMINOPATIA_PASSWORD=tu_contraseña
```

### Crear los archivos Quadlet

Crea el directorio de configuración:

```bash
mkdir -p ~/.config/containers/systemd
```

Copia los archivos `criminopatia.container` y `criminopatia.timer` del repositorio a `~/.config/containers/systemd/`.

**Importante:** En `criminopatia.container`, reemplaza `/home/USER/Criminopatia` con tu ruta real de descargas.

Configura el modo de ejecución descomentando las líneas `Environment=` según necesites:
- `RUN_EPISODES=true` - Episodios regulares
- `RUN_CF=true` - Club de fans (requiere credenciales)
- `RUN_ARCHIVO=true` - Contenido archivado (requiere credenciales)

Si usas la opción B (.env), comenta las líneas `Secret=` y descomenta `EnvironmentFile=`.

### Activar el temporizador

```bash
systemctl --user daemon-reload
systemctl --user enable --now criminopatia.timer
```

### Verificar estado

```bash
# Estado del temporizador
systemctl --user status criminopatia.timer

# Ver próximos ejecuciones
systemctl --user list-timers criminopatia.timer

# Ver registro de ejecuciones pasadas
journalctl --user -u criminopatia.timer
```

### Ejecución manual

Para ejecutar manualmente sin esperar al temporizador:

```bash
podman run --rm criminopatia
```

### Notas importantes

- La bandera `:Z` en el volumen es para SELinux. Si no usas SELinux, puedes quitarla.
- Se recomienda ejecutar manualmente la primera vez para verificar que todo funciona antes de depender del temporizador.
- El temporizador se ejecuta en tu zona horaria local.
- `Persistent=true` asegura que si el sistema estaba apagado cuando debía ejecutarse, correrá inmediatamente al arrancar.

## Instalación local
    git clone https://github.com/ifayost/Criminopatia.git
    cd Crimnopatia
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt
    python3 criminopatia.py -h
