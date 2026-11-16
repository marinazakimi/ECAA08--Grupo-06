"""Verificações independentes e casos de fronteira usados pelos notebooks."""
import math
import random
from itertools import combinations
import scada_arvores as s


def exige_erro(func, tipo=ValueError):
    try: func()
    except tipo: return
    raise AssertionError('A entrada inválida não foi rejeitada')


def teste_19():
    vs = list(s.PONTOS); es = s.arestas_mapa()
    referencia = min(s.custo(a) for a in combinations(es, len(vs)-1) if len(s.componentes(vs, a)) == 1)
    for algoritmo in (s.kruskal, s.prim):
        a, _ = algoritmo(vs, es); s.verificar_floresta(vs, es, a)
        assert math.isclose(s.custo(a), referencia)
        for vertices, arestas in [([], []), (['A'], []), (['A','B','C'], [('A','B',1)]),
                                   (['A','B','C'], [('A','B',1),('A','C',1),('B','C',1)])]:
            a, _ = algoritmo(vertices, arestas); s.verificar_floresta(vertices, arestas, a)
    cortes = [e for e in es if 'T1' not in e[:2]]
    a, _ = s.kruskal(vs, cortes)
    assert len(a) == 4 and len(s.componentes(vs, a)) == 2
    exige_erro(lambda: s.kruskal(['A'], [('A','A',2)]))
    return {'custo_m': referencia, 'vertices': len(vs), 'arestas_admissiveis': len(es)}


def teste_20():
    seq = [e['tipo'] for e in s.gerar_eventos()]
    for x in [[], [0], [3]*41, list(range(6)), seq]:
        assert s.descomprimir(s.comprimir(x)) == x
        assert s.ler_fixo(s.fixo(x)) == x
    p = s.comprimir(seq)
    corrompido = bytearray(p); corrompido[-5] ^= 1
    exige_erro(lambda: s.descomprimir(bytes(corrompido)))
    exige_erro(lambda: s.descomprimir(p[:-1]))
    exige_erro(lambda: s.comprimir([8]))
    _, cod, _ = s.huffman(seq)
    assert all(not b.startswith(a) for a in cod.values() for b in cod.values() if a != b)
    payload = sum(len(cod[x]) for x in seq)
    dicionario = sum(2+(len(c)+7)//8 for c in cod.values())
    assert len(p) == 11+dicionario+(payload+7)//8+4
    assert len(p) < len(s.fixo(seq))
    assert len(s.comprimir([0,1,3,5])) > len(s.fixo([0,1,3,5]))
    return {'eventos':len(seq), 'huffman_bytes':len(p), 'fixo_bytes':len(s.fixo(seq)), 'dicionario_bytes':dicionario}


def teste_21():
    ev = s.gerar_eventos(); ordem = list(ev); random.Random(21).shuffle(ordem)
    arv = s.Historico()
    for e in ordem: arv.inserir(e)
    assert arv.percurso() == ev
    for e in ev: assert arv.buscar((e['instante_ms'],e['id']))[0] == e
    for a,b in [(0,0),(0,5000),(60000,100000),(0,10**9),(10**9,10**9)]:
        assert arv.intervalo(a,b) == [e for e in ev if a <= e['instante_ms'] <= b]
    alerta = next(e for e in ev if e['tipo'] == 4)
    assert len(arv.intervalo(alerta['instante_ms'],alerta['instante_ms'])) == 2
    exige_erro(lambda: arv.inserir(ev[0])); exige_erro(lambda: arv.intervalo(10,0))
    pior = s.Historico()
    for e in ev: pior.inserir(e)
    assert pior.altura() == len(ev)-1
    vazio = s.Historico(); assert vazio.altura() == -1 and vazio.percurso() == []
    # Árvore manual 2 / 1 / 3: referência explícita para os três percursos.
    tres = s.Historico()
    for i in [2,1,3]: tres.inserir(dict(id=i,instante_ms=i,missao='manual'))
    assert [e['id'] for e in tres.percurso('pre')] == [2,1,3]
    assert [e['id'] for e in tres.percurso('pos')] == [1,3,2]
    return {'eventos':len(ev), 'altura_embaralhada':arv.altura(), 'altura_ordenada':pior.altura()}


def colisao_oraculo(a, b, r):
    """Verificador distinto de slabs: orientações contra quatro arestas."""
    def orient(p,q,r): return (q[0]-p[0])*(r[1]-p[1])-(q[1]-p[1])*(r[0]-p[0])
    def pertence(p,q,r):
        return abs(orient(p,q,r)) < 1e-8 and min(p[0],q[0])-1e-8 <= r[0] <= max(p[0],q[0])+1e-8 and min(p[1],q[1])-1e-8 <= r[1] <= max(p[1],q[1])+1e-8
    def cruzam(p,q,r,t):
        a1,a2,b1,b2=orient(p,q,r),orient(p,q,t),orient(r,t,p),orient(r,t,q)
        return (a1*a2 < 0 and b1*b2 < 0) or pertence(p,q,r) or pertence(p,q,t) or pertence(r,t,p) or pertence(r,t,q)
    x0,x1,y0,y1 = r; vertices=[(x0,y0),(x1,y0),(x1,y1),(x0,y1)]
    return s.dentro(a,r) or s.dentro(b,r) or any(cruzam(a,b,p,q) for p,q in zip(vertices,vertices[1:]+vertices[:1]))


def conferir_rrt(res, obstaculos=s.OBSTACULOS):
    if not res['nos']: return
    assert res['pais'][0] is None and len(res['pais']) == len(res['nos'])
    for i,pai in enumerate(res['pais'][1:],1):
        assert 0 <= pai < i
        a,b=res['nos'][pai],res['nos'][i]
        assert math.dist(a,b) <= 10+1e-8
        assert s.livre(a,obstaculos) and s.livre(b,obstaculos)
        assert not any(colisao_oraculo(a,b,s.inflar(r)) for r in obstaculos)
    if res['status'] == 'SUCESSO':
        assert res['caminho'][0] == res['nos'][0]
        for a,b in zip(res['caminho'],res['caminho'][1:]):
            assert not any(colisao_oraculo(a,b,s.inflar(r)) for r in obstaculos)
    else: assert res['caminho'] == []


def teste_22():
    a,b=s.PONTOS['BASE'],s.PONTOS['T1']; res=s.rrt(a,b); conferir_rrt(res)
    assert res['status'] == 'SUCESSO' and res == s.rrt(a,b)
    assert not s.segmento_livre(a,b)
    assert s.rrt(a,a)['caminho'] == [a]
    assert s.rrt(a,b,max_iter=0)['status'] == 'ORCAMENTO_ESGOTADO'
    assert s.rrt((80,50),b)['status'] == 'PONTO_INVALIDO'
    exige_erro(lambda:s.rrt(a,b,passo=0))
    barreira=[(75,95,-20,210)]; fracasso=s.rrt(a,b,max_iter=300,obstaculos=barreira)
    conferir_rrt(fracasso,barreira); assert fracasso['status']=='ORCAMENTO_ESGOTADO'
    for p,q,r,esperado in [((0,0),(2,0),(1,1.1,-1,1),True),((0,1),(2,1),(1,2,1,2),True),
                            ((0,0),(0,2),(1,2,1,2),False),((1.5,1.5),(1.5,1.5),(1,2,1,2),True)]:
        assert s.intersecta(p,q,r)==colisao_oraculo(p,q,r)==esperado
    return {'nos':len(res['nos']),'iteracoes':res['iteracoes'],'comprimento_m':s.comprimento(res['caminho'])}


def teste_23():
    rede=s.spanning_tree(); mst,_=s.kruskal(list(s.BRIDGES),s.LINKS)
    assert rede['raiz']=='SW_SCADA' and s.custo(rede['ativas'])==20 and s.custo(mst)==11
    assert sum(r[2]=='ROOT' for r in rede['portas'])==2
    assert sum(r[2]=='ALTERNATE' for r in rede['portas'])==1
    for i in range(len(s.LINKS)):
        es=s.LINKS[:i]+s.LINKS[i+1:]; novo=s.spanning_tree(es)
        s.verificar_floresta(list(s.BRIDGES),es,novo['ativas'])
    assert s.spanning_tree([])['status']=='PARTICIONADA'
    assert s.convergencia('RSTP')[-1][0] < s.convergencia('STP')[-1][0]
    return {'raiz':rede['raiz'],'custo_stp':s.custo(rede['ativas']),'custo_mst':s.custo(mst)}


def teste_24():
    rede,m0=s.rede_missao(); marcas,arcos,_=s.atingibilidade(rede,m0)
    assert len(marcas)==6 and all(sum(m)==1 and max(m)==1 for m in marcas)
    assert not any(m[2] and m[3] for m in marcas)
    terminais=[m for m in marcas if not any(s.habilitada(m,t[0]) for t in rede.values())]
    assert terminais==[(0,0,0,0,0,1)]
    cov=s.cobertura(rede,m0)
    assert {n['m'] for n in cov}==set(marcas)
    fila={'produzir':((1,0),(1,1)), 'confirmar':((0,1),(0,0))}
    omega=s.cobertura(fila,(1,0)); assert any(n['m']==(1,math.inf) for n in omega)
    assert any(all(x>=y for x,y in zip(n['m'],(1,100))) for n in omega)
    exige_erro(lambda:s.disparar(m0,rede['chegar']))
    exige_erro(lambda:s.atingibilidade(fila,(1,0),limite=12),RuntimeError)
    return {'marcacoes':len(marcas),'arcos':len(arcos),'nos_cobertura_fila':len(omega),'fila_ilimitada':True}


def teste_25():
    bb=dict(aprovada=True,rota_ok=True,na_faixa=True)
    assert s.tick_supervisor(bb,s.telemetria())['bomba']
    for mudanca in [dict(EST_WT_01=9),dict(DRN_ET_01=9),dict(DRN_LT_01=4),dict(gps_ok=False),
                    dict(comm_ok=False),dict(idade_s=3),dict(e_stop=True),dict(alt_ok=False),
                    dict(auto_mode=True,manual_mode=True),dict(DRN_FT_01=float('nan')),
                    dict(is_flying=False)]:
        assert not s.tick_supervisor(dict(aprovada=True,rota_ok=True,na_faixa=True),s.telemetria(**mudanca))['bomba']
    s.tick_supervisor(bb,s.telemetria(DRN_PT_01=5.5,DRN_FT_01=.2))
    assert bb['retida']
    assert not s.tick_supervisor(bb,s.telemetria(bomba_feedback=False,DRN_FT_01=0))['bomba']
    bb['rearme']=True
    assert not s.tick_supervisor(bb,s.telemetria())['bomba'] # falta confirmação
    bb.update(rearme=True,inspecao_confirmada=True)
    assert s.tick_supervisor(bb,s.telemetria())['bomba']
    assert s.tick_supervisor(bb,s.telemetria(DRN_ET_01=15))['acao']=='SOLICITAR_RETORNO'
    assert s.tick_supervisor(bb,s.telemetria(DRN_ET_01=5,gps_ok=False))['acao']=='PAUSAR_DADOS'
    for p,q,b,v,n in [(5,.5,10,8,5),(3,2,20,3,20)]:
        alarmes,ok=s.diagnostico(s.telemetria(DRN_PT_01=p,DRN_FT_01=q,DRN_ET_01=b,EST_WT_01=v,DRN_LT_01=n))
        assert ok and not alarmes
    # Demonstra SUCCESS/FAILURE/RUNNING sem acionar hardware.
    contexto={'trilha':[]}
    seq=s.Composto('seq',[s.Folha('falha',lambda b:s.FAILURE),s.acao('não executar')])
    assert seq.tick(contexto)==s.FAILURE and 'acao' not in contexto
    return {'bloqueios_testados':11,'retencao_e_rearme':'APROVADOS'}


def teste_26():
    rng=random.Random(26); pts=[(i,(rng.uniform(-10,10),rng.uniform(-10,10))) for i in range(400)]
    pts += [(400,(0.,0.)),(401,(0.,0.))]; raiz=s.kd_construir(pts); visitas=[]
    for _ in range(100):
        q=(rng.uniform(-12,12),rng.uniform(-12,12)); esperado=min(pts,key=lambda it:(math.dist(it[1],q),it[0]))
        obtido,n=s.kd_vizinho(raiz,q); visitas.append(n)
        assert obtido[:2]==esperado
        assert s.kd_raio(raiz,q,3)==sorted(i for i,p in pts if math.dist(p,q)<=3)
    assert s.kd_vizinho(raiz,(0,0))[0][0]==400
    assert s.kd_vizinho(None,(0,0))[0] is None and s.kd_raio(None,(0,0),2)==[]
    return {'consultas':100,'pontos':len(pts),'media_nos_visitados':sum(visitas)/len(visitas)}


def teste_27():
    # Instância manual: a melhor divisão separa perfeitamente as duas classes.
    for criterio in ('gini','entropy'):
        no=s.treinar_arvore([[0],[1],[3],[4]],[0,0,1,1],criterio,2,1)
        assert no['limiar']==2 and [s.prever(no,[i]) for i in range(5)]==[0,0,0,1,1]
    assert math.isclose(s.impureza([0,1]),.5) and math.isclose(s.impureza([0,1],'entropy'),1)
    cat=s.id3([('A',),('A',),('B',),('B',)],[0,0,1,1])
    assert s.prever_id3(cat,('B',))==1 and s.prever_id3(cat,('NOVO',))==0
    puro=s.treinar_arvore([[1],[1]],[2,2],min_leaf=1); assert 'feature' not in puro
    exige_erro(lambda:s.prever(puro,[float('nan')]))
    exp=s.experimento_classificacao(); grupos=list(exp['grupos'].values())
    assert all(not set(a)&set(b) for a,b in combinations(grupos,2))
    assert sum(map(sum,exp['teste']['confusao']))==100
    # O modelo nunca participa do permissivo determinístico.
    bb=dict(aprovada=True,rota_ok=True,na_faixa=True,sugestao_ml='NORMAL')
    assert not s.tick_supervisor(bb,s.telemetria(EST_WT_01=9))['bomba']
    return {'escolhido':exp['escolhido'],**exp['teste']}


def teste_28():
    res=s.simular_missao(); l=res['linhas']
    assert [x['bomba'] for x in l]==[False,False,True,False,True,False,False,True,False,True,False,False]
    assert l[6]['alarmes']=='FALHA_RETIDA'
    assert l[-1]['estado_petri']=='CONCLUIDA'
    assert s.custo(res['redes'][8]['ativas'])==11
    assert l[8]['sugestao_ml']=='INDISPONIVEL'
    assert all(not x['bomba'] or x['estado_petri']=='APLICANDO' for x in l)
    return {'ticks':len(l),'eventos':len(res['eventos']),'estado_final':l[-1]['estado_petri'],
            'pacote_huffman_bytes':res['huffman_bytes'],'pacote_fixo_bytes':res['fixo_bytes']}


TESTES={i:globals()[f'teste_{i}'] for i in range(19,29)}
