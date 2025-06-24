import os
import subprocess
import sys

def run_scripts():
    base_dir = os.path.dirname(os.path.abspath(__file__))

    mptt_dir = os.path.join(base_dir, 'mptt')
    treebeard_dir = os.path.join(base_dir, 'treebeard')

    common_scripts = [
        'event_access_units_bench',
        'event_visibility_bench',
        'subgroup_church_bench'
    ]

    print('Executando testes MPTT')
    for script in common_scripts + ['mptt_bench']:
        script_path = os.path.join(mptt_dir, f'{script}.py')
        print(f'Rodando {script_path}')
        subprocess.run([sys.executable, script_path], check=True)

    print('Executando testes Treebeard')
    for script in common_scripts + ['treebeard_bench']:
        script_path = os.path.join(treebeard_dir, f'{script}.py')
        print(f'Rodando {script_path}')
        subprocess.run([sys.executable, script_path], check=True)

if __name__ == "__main__":
    run_scripts()
