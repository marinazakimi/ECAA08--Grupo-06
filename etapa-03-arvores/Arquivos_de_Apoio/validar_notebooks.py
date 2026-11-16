"""Execute: python Arquivos_de_Apoio/validar_notebooks.py

Reexecuta cada notebook em processo Python novo, salva saídas e gera relatório.
Use --jupyter para usar kernels Jupyter em um ambiente que permita sockets locais.
Não altera arquivos das Etapas 1 ou 2.
"""
from datetime import datetime, timezone
import json
from pathlib import Path
import platform
import re
import time
import argparse
import base64
import contextlib
import io
import os
import subprocess
import sys
import types
import nbformat
from nbclient import NotebookClient
import matplotlib


def executar_sequencial(path):
    matplotlib.use('Agg')
    import matplotlib.pyplot as plt
    nb=nbformat.read(path,as_version=4)
    os.chdir(path.parent)
    modulo=types.ModuleType('notebook_validacao');sys.modules[modulo.__name__]=modulo
    contador=0
    for cell in nb.cells:
        if cell.cell_type!='code':continue
        contador+=1; cell.execution_count=contador;cell.outputs=[];captura=io.StringIO()
        def texto():
            valor=captura.getvalue()
            if valor:cell.outputs.append(nbformat.v4.new_output('stream',name='stdout',text=valor))
            captura.seek(0);captura.truncate(0)
        def show(*args,**kwargs):
            texto()
            for num in plt.get_fignums():
                fig=plt.figure(num);data=io.BytesIO();fig.savefig(data,format='png',dpi=120,bbox_inches='tight')
                cell.outputs.append(nbformat.v4.new_output('display_data',data={'image/png':base64.b64encode(data.getvalue()).decode(),'text/plain':'Figura da simulação SCADA'}))
                plt.close(fig)
        plt.show=show
        with contextlib.redirect_stdout(captura),contextlib.redirect_stderr(captura):
            exec(compile(cell.source,f'{path.name}:celula{contador}','exec'),modulo.__dict__)
        texto()
    nb.metadata.language_info={'name':'python','version':platform.python_version()}
    nbformat.validate(nb);nbformat.write(nb,path)


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--arquivo',type=Path)
    parser.add_argument('--jupyter',action='store_true')
    args=parser.parse_args()
    if args.arquivo:
        executar_sequencial(args.arquivo.resolve());return
    apoio=Path(__file__).resolve().parent; etapa=apoio.parent
    catalogo=json.loads((apoio/'catalogo_aulas.json').read_text(encoding='utf-8'))
    resultados={}; total=0
    for aula in catalogo:
        p=etapa/(aula['stem']+'.ipynb')
        nb=nbformat.read(p,as_version=4);nbformat.validate(nb)
        inicio=time.perf_counter()
        if args.jupyter:
            NotebookClient(nb,timeout=180,kernel_name='python3',resources={'metadata':{'path':str(etapa)}}).execute()
            nbformat.validate(nb); nbformat.write(nb,p)
        else:
            subprocess.run([sys.executable,str(Path(__file__).resolve()),'--arquivo',str(p)],check=True)
            nb=nbformat.read(p,as_version=4)
        cells=[c for c in nb.cells if c.cell_type=='code'];total+=len(cells)
        resumo=None
        for c in cells:
            if c.source.startswith('RESUMO = TESTES['):
                texto=''.join(o.get('text','') for o in c.outputs if o.output_type=='stream')
                resumo=json.JSONDecoder().raw_decode(texto)[0]
        assert resumo is not None and all(c.execution_count for c in cells)
        resultados[str(aula['numero'])]={'celulas_codigo':len(cells),'segundos':round(time.perf_counter()-inicio,3),
                                       'status':'APROVADO','resumo':resumo}
        print(aula['numero'],'APROVADO',len(cells),'células',flush=True)
    rel={'executado_em_utc':datetime.now(timezone.utc).isoformat(),'python':platform.python_version(),
         'matplotlib':matplotlib.__version__,'nbformat':nbformat.__version__,
         'metodo':('nbclient: kernel Python novo por notebook' if args.jupyter else 'células sequenciais em processo Python novo por notebook; formato validado com nbformat'),
         'celulas_codigo':total,'aulas':resultados}
    (apoio/'Resultados_Validacao.json').write_text(json.dumps(rel,ensure_ascii=False,indent=2),encoding='utf-8')
    texto='# Relatório de validação — Etapa 3 SCADA\n\n'
    texto+=f"Método: {rel['metodo']}. Python {rel['python']}; Matplotlib {rel['matplotlib']}.\n\n"
    texto+=f"Executados 10 notebooks, total de **{total} células de código**, sem erros. Saídas e figuras salvas nos notebooks.\n\n"
    texto+='| Aula | Células de código | Resultado |\n|---|---:|---|\n'
    for k,v in resultados.items():texto+=f"| {k} | {v['celulas_codigo']} | {v['status']} |\n"
    texto+='\nOs critérios estão em [verificacoes.py](verificacoes.py). Resultados quantitativos e ambiente: [Resultados_Validacao.json](Resultados_Validacao.json).\n\n'
    texto+='A validação cobre os modelos didáticos; não comprova capacidade de voo, segurança funcional certificada ou funcionamento de dispositivos físicos.\n'
    (apoio/'Relatorio_de_Validacao.md').write_text(texto,encoding='utf-8')
    print('TOTAL:',total,'células de código aprovadas.')


if __name__=='__main__':main()
