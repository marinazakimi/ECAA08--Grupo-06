"""Recria os dados do replay e a HMI local a partir dos algoritmos da etapa."""
from pathlib import Path
import csv, json
import scada_arvores as s
import visualizacao as v
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parent

def csv_salvar(nome, linhas):
    with (ROOT/nome).open('w',encoding='utf-8',newline='') as f:
        writer=csv.DictWriter(f,fieldnames=list(linhas[0]));writer.writeheader();writer.writerows(linhas)

def main():
    resultado=s.simular_missao()
    csv_salvar('Telemetria_Simulacao.csv',resultado['linhas'])
    csv_salvar('Historico_Simulacao.csv',resultado['eventos'])
    dados=s.dados_classificacao(amostras=20)
    csv_salvar('Dados_Classificacao.csv',[dict(missao=d['missao'],particao='treino' if d['missao']%6<4 else ('validacao' if d['missao']%6==4 else 'teste'),**dict(zip(s.FEATURES,d['x'])),classe=s.CLASSES[d['y']]) for d in dados])
    v.arquitetura();plt.close('all')
    payload=json.dumps(resultado['linhas'],ensure_ascii=False)
    html='''<!doctype html><html lang="pt-BR"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>SCADA • Drone agrícola | Grupo 06</title>
<style>*{box-sizing:border-box}body{margin:0;background:#f1f5f6;color:#16394c;font:16px system-ui}header{background:#16394c;color:white;padding:28px}main{max-width:1150px;margin:auto;padding:24px}h1{font-size:26px;margin:8px 0}h2{font-size:20px}small{color:inherit}.controls,section{background:white;border-radius:12px;padding:20px;margin-bottom:18px}.grid{display:grid;grid-template-columns:repeat(5,1fr);gap:12px}.card{padding:18px;background:#eaf4f2;border-radius:8px}.card b{display:block;font-size:25px;margin-top:10px}.details{display:grid;grid-template-columns:1fr 1fr;gap:20px}button{padding:10px 16px;border:0;border-radius:6px;background:#008579;color:white;cursor:pointer}input{width:55%;vertical-align:middle}table{border-collapse:collapse;width:100%;font-size:13px}td,th{padding:10px;border-bottom:1px solid #ddd;text-align:left}tr.selected{background:#e1f3ec}.table{overflow:auto}.alarm{color:#ac4c13;font-weight:600}p{line-height:1.55}@media(max-width:750px){.grid{grid-template-columns:repeat(2,1fr)}.details{grid-template-columns:1fr}input{width:90%}}</style>
<header><small>ECAA08 • ARQUITETURA DE SISTEMAS SCADA • GRUPO 06</small><h1>Sistema SCADA aplicado a um Drone Agrícola de Pulverização</h1><div>Etapa 3 — Planejamento e execução supervisionada de missões</div></header>
<main><p><strong>Replay didático de dados simulados.</strong> Os controles navegam nos 12 snapshots calculados em Python. Não enviam comandos a equipamentos. Um tick não representa um segundo de voo.</p>
<div class="controls"><button id="prev">Anterior</button> <button id="next">Próximo</button> <input id="slider" type="range" min="0" max="11" value="0" aria-label="Snapshot"> <strong id="tick"></strong></div>
<section><h2 id="description"></h2><div class="grid" id="cards"></div></section>
<div class="details"><section><h2>Supervisão e permissivos</h2><p>Ação: <strong id="action"></strong></p><p>Solicitação à bomba: <strong id="pump"></strong></p><p>Alarmes: <span class="alarm" id="alarms"></span></p><p>A falha hidráulica permanece retida até inspeção e rearme. Telemetria indisponível bloqueia a pulverização.</p></section><section><h2>Estado e apoio à decisão</h2><p>Marcação de Petri: <strong id="state"></strong></p><p>Transição: <strong id="transition"></strong></p><p>Ponto mais próximo (KD): <strong id="near"></strong></p><p>Sugestão da árvore aprendida: <strong id="ml"></strong></p><small>A classificação é consultiva; não autoriza a bomba.</small></section></div>
<section class="table"><h2>Histórico do replay</h2><table><thead><tr><th>Tick</th><th>Evento do cenário</th><th>Ação</th><th>Estado</th><th>Bomba</th></tr></thead><tbody id="rows"></tbody></table></section>
<p>Arthur, Caique, Luis Felipe e Marina • Dados e algoritmos em Arquivos_de_Apoio. Para reproduzir: executar o notebook 28 ou gerar_apoio.py. O painel funciona sem internet.</p></main>
<script>const data=__DATA__;const get=id=>document.getElementById(id);const slider=get('slider');
get('rows').innerHTML=data.map(r=>`<tr id="row${r.tick}"><td>${r.tick}</td><td>${r.descricao}</td><td>${r.acao}</td><td>${r.estado_petri}</td><td>${r.bomba?'SOLICITADA':'BLOQUEADA'}</td></tr>`).join('');
function render(){const i=Number(slider.value),r=data[i];get('tick').textContent=`${i+1} / ${data.length}`;get('description').textContent=r.descricao;get('cards').innerHTML=[['Bateria',r.bateria,'%'],['Calda',r.nivel,'%'],['Pressão',r.pressao,'bar'],['Vazão',r.vazao,'L/min'],['Vento',r.vento,'m/s']].map(([n,v,u])=>`<div class="card">${n}<b>${v} <small>${u}</small></b></div>`).join('');for(const [id,key] of [['action','acao'],['alarms','alarmes'],['state','estado_petri'],['transition','transicao'],['near','ponto_proximo'],['ml','sugestao_ml']])get(id).textContent=r[key];get('pump').textContent=r.bomba?'PULVERIZAÇÃO SOLICITADA':'DESLIGADA / BLOQUEADA';data.forEach((_,j)=>get('row'+j).classList.toggle('selected',j===i));get('prev').disabled=i===0;get('next').disabled=i===data.length-1;}
slider.addEventListener('input',render);get('prev').onclick=()=>{slider.value=Math.max(0,Number(slider.value)-1);render()};get('next').onclick=()=>{slider.value=Math.min(data.length-1,Number(slider.value)+1);render()};render();</script></html>'''
    (ROOT/'Painel_SCADA.html').write_text(html.replace('__DATA__',payload),encoding='utf-8')
    print('Arquitetura, três CSVs e painel de replay gerados.')
if __name__=='__main__':main()
