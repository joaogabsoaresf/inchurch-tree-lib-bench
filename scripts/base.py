import os
import sys
import logging
import inspect
import time
import django


def setup_sys_path(project_root=None):
    """
    Adiciona o caminho do projeto no sys.path para importar módulos Django.
    Se project_root não for passado, usa o diretório pai do script chamador.
    """
    if project_root is None:
        caller_frame = inspect.stack()[1]
        caller_file = caller_frame.filename
        project_root = os.path.dirname(os.path.dirname(caller_file))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)


def setup_django(settings_module='config.settings'):
    """
    Configura o ambiente Django.
    Recebe o módulo de settings (string).
    """
    if not os.environ.get('DJANGO_SETTINGS_MODULE'):
        os.environ.setdefault('DJANGO_SETTINGS_MODULE', settings_module)
    django.setup()


def setup_logger(additional_dir=None):
    """
    Configura logger com nome do arquivo de log baseado no script chamador.
    Cria a pasta 'logs' no diretório pai do script, se não existir.
    Retorna o logger configurado.
    """
    caller_frame = inspect.stack()[1]
    caller_file = caller_frame.filename
    script_name = os.path.splitext(os.path.basename(caller_file))[0]

    logs_dir = os.path.join(os.path.dirname(caller_file), '..', 'logs')
    if additional_dir:
        logs_dir = os.path.join(logs_dir, additional_dir)

    os.makedirs(logs_dir, exist_ok=True)
    log_path = os.path.join(logs_dir, f"{script_name}.log")

    logging.basicConfig(
        filename=log_path,
        level=logging.INFO,
        format='%(asctime)s [%(levelname)s] %(message)s',
    )
    return logging.getLogger()


def timed(func):
    """
    Decorador para medir o tempo de execução de funções.
    Retorna uma tupla (resultado, duração_em_segundos).
    """
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        result = func(*args, **kwargs)
        duration = time.perf_counter() - start
        return result, duration
    return wrapper
