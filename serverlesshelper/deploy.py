from pathlib import Path
import json
from glob import glob
from ruamel.yaml import YAML
from prompt_toolkit import prompt
from prompt_toolkit.completion import FuzzyWordCompleter
import os
from prompt_toolkit.history import FileHistory
import concurrent.futures


files_map = {}


def get_function_names(path):
    yaml = YAML()
    with open(path, 'r') as stream:
        data_loaded = yaml.load(stream)
        dir_name = path.split('/')[-2]
        files_map[dir_name] = {
            "dir": '/'.join(path.split('/')[0:-1]),
            "is_dir": True
        }

        for key in data_loaded.get('functions', []):
            events = data_loaded['functions'][key].get('events', [])
            route = ''
            if len(events):
                route = events[0].get('httpApi', {}).get('path', {})

            files_map[f'{key} ({dir_name})'] = {
                "name": key,
                "path": path,
                "route": route,
                "dir": '/'.join(path.split('/')[0:-1]),

            }


def deploy():
    stage = os.getenv('STAGE')
    if not stage:
        print('STAGE is not set')
        exit(1)

    home_dir = Path.home()
    config_path = home_dir / '.serverless-helper.json'
    base_dir = ''
    try:
        with open(config_path, 'r') as file:
            json_object = json.load(file)
            base_dir = json_object['base_dir']
    except FileNotFoundError:
        base_dir = prompt('Base directory path: ')
        config_path.write_text(json.dumps({'base_dir': base_dir}))

    paths = glob(f'{base_dir}/*/serverless.y*ml', recursive=True)

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        executor.map(get_function_names, paths)

    function_completer = FuzzyWordCompleter(
        list(files_map.keys()))
    function_name = prompt(
        'function: ', completer=function_completer, complete_while_typing=True, history=FileHistory('/tmp/.serverlesshelper-deploy-history'))

    if not len(function_name):
        os.system(f'make deploy')
    else:
        func = files_map[function_name]

        if func.get('is_dir'):
            os.system(
                f'(cd {func["dir"]} && make deploy)')
        else:
            os.system(
                f'(cd {func["dir"]} && serverless deploy function -f {func["name"]} --stage {stage})')
