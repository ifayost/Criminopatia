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

## Instalación
    git clone https://github.com/ifayost/Criminopatia.git
    cd Crimnopatia
    python3 -m venv .venv
    source .venv/bin/activate
    python3 -m pip install -r requirements.txt
    python3 steganography.py -h
Para logearte usando tus credenciales modifica el usarname y password del archivo credentials.py
