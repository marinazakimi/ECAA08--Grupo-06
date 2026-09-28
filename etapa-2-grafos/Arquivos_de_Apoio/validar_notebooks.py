"""Execute: python validar_notebooks.py

Reexecuta as células de código de cada notebook desta pasta em um namespace
novo, na ordem em que aparecem, sem modificar arquivos. Biblioteca padrão.
É uma verificação Python; não simula a interface gráfica do Jupyter/Colab.
"""
from pathlib import Path
import ast
import contextlib
import io
import json


def main():
    pasta=Path(__file__).resolve().parent
    arquivos=sorted(pasta.glob('[1][1-8]_*.ipynb'))
    if len(arquivos)!=8:
        raise RuntimeError('Esperados os oito notebooks 11 a 18 nesta pasta')
    total=0
    for arquivo in arquivos:
        nb=json.loads(arquivo.read_text(encoding='utf-8'))
        if nb['nbformat']!=4:
            raise RuntimeError('Formato inesperado: '+arquivo.name)
        namespace={'__name__':'__main__'}
        n=0
        for c in nb['cells']:
            if c['cell_type']!='code': continue
            codigo=''.join(c['source'])
            ast.parse(codigo)
            with contextlib.redirect_stdout(io.StringIO()):
                exec(compile(codigo,arquivo.name,'exec'),namespace)
            n+=1
        total+=n
        print(f'PASSOU | {arquivo.name} | {n} células de código')
    print(f'Concluído: {len(arquivos)} notebooks, {total} células, sem exceções.')


if __name__=='__main__':
    main()
