import os
import sys


if __name__ == "__main__":
    # Extrae el path ejecutado sin 'main.py'
    path = '/'.join(sys.argv[0].split('/')[:-1] + [''])
    # Ejecuta '__init_.py' ubicado en el mismo path que 'main.py'
    os.system(f'python3 {path}__init__.py {sys.argv[-1]}')
