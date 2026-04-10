# fmt: off

############################################################
#                    IMPORTAR LIBRERIAS                   #
############################################################

# Librerias
import json

############################################################
#                         FUNCIONES                        #
############################################################


def error_log(title, data=None):
    green = "\033[92m"  # Código ANSI para color verde
    reset = "\033[0m"  # Código ANSI para resetear el color

    if data is None:
        print()
        print(f"{green}{title}{reset}")  # Mostrar título en verde
    else:
        # Validar que se pueda convertir a un string en formato JSON
        try:
            # json.dumps: Convierte un objeto JSON a un string en formato JSON
            #
            # ensure_ascii: Controla cómo se representan los caracteres no ASCII (acentos, ñ, símbolos, etc.)
            #
            # ensure_ascii=True: Todos los caracteres no ASCII (acentos, ñ, símbolos, etc.) se convierten a secuencias \uXXXX
            # Ejemplo: "rápido" → "r\u00e1pido"
            #
            # ensure_ascii=False: Mantiene los caracteres tal cual en la cadena resultante
            # Ejemplo: "rápido" → "rápido"
            data = json.dumps(data, ensure_ascii=False)
        except (TypeError, OverflowError):
            data = data

        print()
        print(f"{green}{title} -- {data}{reset}")  # Mostrar título y data en verde
