"""Figuras originais geradas dos modelos; gravação em caminhos relativos ao módulo."""
from pathlib import Path
import math
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, FancyBboxPatch
import scada_arvores as s

IMAGENS=Path(__file__).resolve().parent/'Imagens'
AZUL,VERDE,LARANJA,CINZA='#16394C','#008579','#D36E2E','#9BA9B2'
plt.rcParams.update({'font.size':10,'axes.spines.top':False,'axes.spines.right':False,
                     'axes.titleweight':'bold','figure.dpi':110})


def salvar(fig,nome):
    IMAGENS.mkdir(exist_ok=True)
    fig.savefig(IMAGENS/nome,dpi=150,bbox_inches='tight',facecolor='white')
    return fig


def mapa(ax):
    for i,r in enumerate(s.OBSTACULOS):
        for caixa,alpha in [(s.inflar(r),.16),(r,.65)]:
            x0,x1,y0,y1=caixa
            ax.add_patch(Rectangle((x0,y0),x1-x0,y1-y0,color=LARANJA,alpha=alpha))
    for nome,p in s.PONTOS.items():
        ax.scatter(*p,color=AZUL,s=30,zorder=5);ax.annotate(nome,p,xytext=(5,5),textcoords='offset points')
    x0,x1,y0,y1=s.LIMITES; r=s.MARGEM
    ax.add_patch(Rectangle((x0+r,y0+r),x1-x0-2*r,y1-y0-2*r,fill=False,ls='--',ec=CINZA))
    ax.set(xlim=(x0-5,x1+5),ylim=(y0-5,y1+5),xlabel='x (m)',ylabel='y (m)')
    ax.set_aspect('equal');ax.grid(alpha=.12)


def ligacoes(ax,arestas,enumerar=False):
    for i,(u,v,w) in enumerate(arestas,1):
        a,b=s.PONTOS[u],s.PONTOS[v]
        ax.plot([a[0],b[0]],[a[1],b[1]],color=VERDE,lw=2)
        if enumerar:
            ax.text((a[0]+b[0])/2,(a[1]+b[1])/2,str(i),ha='center',va='center',color='white',
                    bbox=dict(boxstyle='circle,pad=.2',fc=AZUL,ec='none'))


def arvore(ax,raiz,filhos,rotulo,titulo='',fontsize=9):
    """Layout por folhas, sem dependência de Graphviz."""
    pos={}; nodes={}; links=[]; cursor=[0]
    def visitar(no,depth=0):
        ident=id(no); nodes[ident]=no; fs=filhos(no)
        xs=[]
        for label,f in fs:
            x=visitar(f,depth+1);xs.append(x);links.append((ident,id(f),label))
        if xs:x=sum(xs)/len(xs)
        else:x=cursor[0];cursor[0]+=1
        pos[ident]=(x,-depth);return x
    if raiz is None:ax.text(.5,.5,'Árvore vazia',ha='center');ax.axis('off');return
    visitar(raiz)
    for a,b,label in links:
        x,y=pos[a];u,v=pos[b]
        ax.plot([x,u],[y,v],color=CINZA,zorder=1)
        if label:ax.text((x+u)/2,(y+v)/2,label,color=LARANJA,fontsize=8,ha='center')
    for ident,(x,y) in pos.items():
        ax.text(x,y,rotulo(nodes[ident]),ha='center',va='center',fontsize=fontsize,zorder=2,
                bbox=dict(boxstyle='round,pad=.35',fc='white',ec=VERDE))
    ax.set_xlim(-.8,max(1,cursor[0]-.2));ax.set_ylim(min(y for x,y in pos.values())-.6,.6)
    ax.axis('off');ax.set_title(titulo)


def arquitetura():
    fig,ax=plt.subplots(figsize=(11,8));ax.set(xlim=(0,10),ylim=(0,10));ax.axis('off')
    boxes=[(0.4,7.5,4,1.3,'CAMPO • DRONE\nNível, pressão, vazão, bateria, GNSS\nBomba e válvulas dos bicos'),
           (5.6,7.5,4,1.3,'CAMPO • ESTAÇÃO DE SOLO\nPreparo, abastecimento e vento\nSensores e atuadores locais'),
           (2.5,5.4,5,1.2,'AQUISIÇÃO / CONTROLE LOCAL\nRTU e controladora embarcada\nTelemetria; validação local de comandos'),
           (2.5,2.9,5,1.5,'SERVIDOR SCADA\nAlarmes • histórico • apoio ao planejamento\nÁrvores da Etapa 3\nLAN redundante na estação de solo'),
           (2.5,.5,5,1.3,'HMI / OPERADOR\nMapa, tendências e alarmes\nAprovação e registro de decisões')]
    for x,y,w,h,label in boxes:
        ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle='round,pad=.1',fc='#EFF6F5',ec=VERDE,lw=1.5))
        ax.text(x+w/2,y+h/2,label,ha='center',va='center',fontsize=11,color=AZUL)
    for a,b in [((2.4,7.4),(4,6.7)),((7.6,7.4),(6,6.7)),((4.5,5.3),(4.5,4.5)),((5.5,4.5),(5.5,5.3)),((4.5,2.8),(4.5,1.9)),((5.5,1.9),(5.5,2.8))]:
        ax.annotate('',xy=b,xytext=a,arrowprops=dict(arrowstyle='->',color=AZUL,lw=1.8))
    ax.text(2.2,4.9,'Rádio / Wi-Fi',ha='right',fontsize=10)
    ax.text(7.9,4.9,'Solicitação +\nconfirmação',fontsize=10)
    ax.set_title('Sistema SCADA aplicado a um Drone Agrícola de Pulverização',pad=20)
    return salvar(fig,'00_Arquitetura_SCADA.png')


def figura19():
    es=s.arestas_mapa();k,_=s.kruskal(list(s.PONTOS),es);p,_=s.prim(list(s.PONTOS),es)
    fig,axes=plt.subplots(1,3,figsize=(15,5),constrained_layout=True)
    for ax,titulo,a in zip(axes,['Conexões admissíveis','Kruskal','Prim'],[es,k,p]):
        mapa(ax);ligacoes(ax,a,titulo!='Conexões admissíveis')
        ax.set_title(titulo+'\n'+(f'{len(a)} arestas' if a==es else f'{s.custo(a):.3f} m'))
    fig.suptitle('SCADA • Referência de conectividade entre base e acessos aos talhões',color=AZUL)
    return salvar(fig,'19_Arvores_Geradoras.png')


def figura20():
    seq=[e['tipo'] for e in s.gerar_eventos()];root,cod,_=s.huffman(seq)
    fig,axes=plt.subplots(1,2,figsize=(14,6),constrained_layout=True)
    arvore(axes[0],root,lambda n:[] if 's' in n else [('0',n['esq']),('1',n['dir'])],
           lambda n:f"{n['s']} | {n['f']}\n{cod[n['s']]}" if 's' in n else str(n['f']), 'Huffman • tipo | frequência | código')
    casos=[seq,[0,1,3,5],list(range(6))*10];x=list(range(3))
    axes[1].bar([i-.18 for i in x],[len(s.fixo(c)) for c in casos],.36,label='Fixo + CRC',color=AZUL)
    axes[1].bar([i+.18 for i in x],[len(s.comprimir(c)) for c in casos],.36,label='Huffman + dicionário + CRC',color=VERDE)
    axes[1].set(xticks=x,xticklabels=['Histórico','Curta','Equilibrada'],ylabel='Bytes por pacote',title='Economia líquida, incluindo metadados')
    axes[1].legend(fontsize=9)
    return salvar(fig,'20_Huffman_e_Pacotes.png')


def figura21():
    import random
    eventos=s.gerar_eventos()[:12];mix=list(eventos);random.Random(21).shuffle(mix)
    fig,axes=plt.subplots(1,3,figsize=(14,7),constrained_layout=True)
    for ax,seq,nome in zip(axes,[mix,eventos,s.ordem_mediana(eventos)],['Embaralhada','Cronológica','Mediana-primeiro']):
        bst=s.Historico()
        for e in seq:bst.inserir(e)
        arvore(ax,bst.raiz,lambda n:[(l,f) for l,f in [('E',n.esq),('D',n.dir)] if f],
               lambda n:str(n.evento['id']),nome+f' • altura {bst.altura()}')
        ax.set_ylim(-12,.7)
    fig.suptitle('Historiador SCADA • 12 ocorrências ilustrativas (rótulos = IDs)',color=AZUL)
    return salvar(fig,'21_Arvores_do_Historico.png')


def figura22(res=None):
    res=res or s.rrt(s.PONTOS['BASE'],s.PONTOS['T1']);n=len(res['nos'])
    fig,axes=plt.subplots(2,2,figsize=(11,10),constrained_layout=True)
    for ax,limite in zip(axes.flat,[n//4,n//2,n,n]):
        mapa(ax)
        for i,p in enumerate(res['pais'][1:limite],1):
            a,b=res['nos'][p],res['nos'][i];ax.plot([a[0],b[0]],[a[1],b[1]],color=CINZA,lw=.8)
        ax.set_title(f'{limite} nós aceitos')
    ax=axes[1,1];path=res['caminho']
    ax.plot([p[0] for p in path],[p[1] for p in path],color=VERDE,lw=3)
    ax.set_title(f'Caminho validado • {s.comprimento(path):.2f} m')
    fig.suptitle('SCADA • Proposta de deslocamento com margem de 2 m',color=AZUL)
    return salvar(fig,'22_Crescimento_RRT.png')


def figura23():
    fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    pos={'SW_SCADA':(0,2),'SW_HMI':(-1,0),'SW_RADIO':(1,0)}
    for ax,links,titulo in zip(axes,[s.LINKS,s.LINKS[:1]+s.LINKS[2:]],['LAN estável • um enlace bloqueado','Após falha SCADA–RÁDIO']):
        r=s.spanning_tree(links);ativas={frozenset(e[:2]) for e in r['ativas']}
        for u,v,w in links:
            a,b=pos[u],pos[v];ok=frozenset((u,v)) in ativas
            ax.plot([a[0],b[0]],[a[1],b[1]],color=VERDE if ok else LARANJA,ls='-' if ok else '--',lw=3)
            ax.text((a[0]+b[0])/2,(a[1]+b[1])/2,str(w),bbox=dict(fc='white',ec='none'))
        for nome,(x,y) in pos.items():
            ax.text(x,y,nome.replace('_','\n'),ha='center',va='center',bbox=dict(fc='#EFF6F5',ec=AZUL,boxstyle='round,pad=.5'))
        ax.text(0,2.5,'ROOT BRIDGE',ha='center',color=VERDE)
        ax.set(xlim=(-1.7,1.7),ylim=(-.8,3));ax.axis('off');ax.set_title(titulo)
    fig.suptitle('SCADA • Rede Ethernet da estação de solo (custos abstratos de porta)',color=AZUL)
    return salvar(fig,'23_LAN_STP_RSTP.png')


def figura24():
    fig,axes=plt.subplots(1,2,figsize=(13,6),constrained_layout=True)
    pos={0:(0,2),1:(0,1),2:(0,0),3:(1.5,0),4:(0,-1),5:(0,-2)}
    for nome,a,b in s.ARCOS:
        xy,posb=pos[a],pos[b]
        curve=.18 if (a,b) in [(2,3),(3,2)] else (.65 if (a,b)==(1,4) else 0)
        axes[0].annotate('',xy=posb,xytext=xy,arrowprops=dict(arrowstyle='->',color=CINZA,connectionstyle=f'arc3,rad={curve}',shrinkA=25,shrinkB=25))
        label_pos={(2,3):(.75,-.32),(3,2):(.75,.32),(1,4):(-.95,.15),(3,4):(1.25,-.75)}
        lx,ly=label_pos.get((a,b),((xy[0]+posb[0])/2+.08,(xy[1]+posb[1])/2+.10))
        axes[0].text(lx,ly,nome.replace('_','\n'),fontsize=7,color=LARANJA)
    for i,(x,y) in pos.items():axes[0].text(x,y,f'M{i}\n{s.LUGARES[i]}',ha='center',va='center',fontsize=9,bbox=dict(fc='white',ec=VERDE,boxstyle='round'))
    axes[0].set(xlim=(-1,3),ylim=(-2.6,2.6),title='Grafo de atingibilidade • um token');axes[0].axis('off')
    nodes=s.cobertura({'produzir':((1,0),(1,1)),'confirmar':((0,1),(0,0))},(1,0))
    def filhos(n):return [(v['via'],v) for v in nodes if v['pai']==nodes.index(n)]
    arvore(axes[1],nodes[0],filhos,lambda n:'('+', '.join('ω' if math.isinf(x) else str(x) for x in n['m'])+')'+('\nrepetido' if n['repetido'] else ''),'Cobertura • (produtor, fila de eventos)')
    return salvar(fig,'24_Petri_e_Cobertura.png')


def figura24_arvore():
    rede,m=s.rede_missao(); nodes=s.arvore_atingibilidade(rede,m)
    fig,ax=plt.subplots(figsize=(13,7),constrained_layout=True)
    def filhos(n):return [(v['via'].replace('_','\n'),v) for v in nodes if v['pai']==nodes.index(n)]
    arvore(ax,nodes[0],filhos,lambda n:s.LUGARES[n['m'].index(1)]+('\nrepetido' if n['repetido'] else ''),
           'Árvore de atingibilidade • repetição encerrada em folha',fontsize=9)
    return salvar(fig,'24_Arvore_Atingibilidade.png')


def figura25():
    # Fluxo de prioridade fiel à ordem do seletor; não sugere execução paralela.
    nomes=['Emergência','Qualidade de dados','Bateria crítica','Bloqueios e retenção','Conclusão / aprovação',
           'Retorno / planejamento','Deslocamento / voo','Pulverização permitida']
    acoes=['EMERGENCIA','PAUSAR_DADOS','INTERROMPER_MISSAO','PAUSAR','CONCLUIR / AGUARDAR',
           'SOLICITAR_RETORNO / PLANEJAR','DESLOCAR / AGUARDAR_VOO','PULVERIZAR']
    fig,ax=plt.subplots(figsize=(10,9));ax.axis('off');ax.set(xlim=(0,10),ylim=(-.7,8.5))
    for i,(nome,acao) in enumerate(zip(nomes,acoes)):
        y=7-i
        ax.text(2.5,y,nome,ha='center',va='center',bbox=dict(fc='#EFF6F5',ec=VERDE,boxstyle='round,pad=.5'))
        ax.text(7,y,acao,ha='center',va='center',fontsize=9,bbox=dict(fc='white',ec=AZUL,boxstyle='round,pad=.5'))
        ax.annotate('',xy=(5.3,y),xytext=(4.1,y),arrowprops=dict(arrowstyle='->',color=AZUL))
        if i<7:ax.annotate('',xy=(2.5,y-.72),xytext=(2.5,y-.25),arrowprops=dict(arrowstyle='->',color=CINZA))
    ax.set_title('SCADA • Ordem do seletor reativo\nCada tick reavalia a prioridade; ações retornam status',pad=20)
    return salvar(fig,'25_Prioridades_Comportamento.png')


def figura26():
    pts=list(enumerate(s.PONTOS.values()));kd=s.kd_construir(pts);q=(150,85);viz,_=s.kd_vizinho(kd,q)
    fig,axes=plt.subplots(1,2,figsize=(12,5),constrained_layout=True)
    arvore(axes[0],kd,lambda n:[(l,f) for l,f in [('E',n.esq),('D',n.dir)] if f],
           lambda n:f"{list(s.PONTOS)[n.id]}\n{'x' if n.eixo==0 else 'y'}={n.ponto[n.eixo]}",'KD-Tree • divisão alternada por eixo')
    mapa(axes[1]);axes[1].scatter(*q,marker='x',s=90,color=LARANJA,label='Consulta')
    p=viz[1];axes[1].plot([q[0],p[0]],[q[1],p[1]],'--',color=VERDE)
    axes[1].set_title('Vizinho geométrico mais próximo');axes[1].legend()
    return salvar(fig,'26_KD_Tree.png')


def figura27(exp):
    fig,ax=plt.subplots(figsize=(14,7),constrained_layout=True)
    arvore(ax,exp['modelo'],lambda n:[] if 'feature' not in n else [('≤',n['esq']),('>',n['dir'])],
           lambda n:(s.FEATURES[n['feature']]+f"\n≤ {n['limiar']:.2f}\nn={n['n']}") if 'feature' in n else s.CLASSES[n['classe']].replace('_','\n')+f"\nn={n['n']}",
           'SCADA • Classificação consultiva aprendida de dados sintéticos',fontsize=8)
    return salvar(fig,'27_Arvore_Aprendida.png')


def figura28(res):
    fig,axes=plt.subplots(2,2,figsize=(13,9),constrained_layout=True);l=res['linhas'];x=[r['tick'] for r in l]
    mapa(axes[0,0]);p=res['rota']['caminho'];axes[0,0].plot([a[0] for a in p],[a[1] for a in p],color=VERDE,lw=2)
    axes[0,0].set_title('Proposta de trajeto aprovada no cenário')
    for campo,cor in [('bateria',AZUL),('nivel',VERDE)]:axes[0,1].plot(x,[r[campo] for r in l],marker='o',label=campo,color=cor)
    axes[0,1].set(title='Telemetria simulada',xlabel='Tick',ylabel='%');axes[0,1].legend()
    axes[1,0].step(x,[int(r['bomba']) for r in l],where='mid',color=VERDE,lw=3)
    axes[1,0].set(title='Solicitação final de aplicação',xlabel='Tick',ylabel='Bomba (0/1)',yticks=[0,1],ylim=(-.1,1.2))
    for i in [3,5,6,8]:axes[1,0].axvspan(i-.4,i+.4,color=LARANJA,alpha=.15)
    axes[1,1].axis('off')
    texto='HISTÓRICO DE DECISÕES\n\n'+'\n'.join(f"{r['tick']:02d}  {r['acao']}" for r in l)
    axes[1,1].text(.02,.98,texto,va='top',fontfamily='monospace',fontsize=10,color=AZUL)
    fig.suptitle('HMI didática • Sistema SCADA do Drone Agrícola • Replay, sem hardware',color=AZUL)
    return salvar(fig,'28_Painel_SCADA.png')
