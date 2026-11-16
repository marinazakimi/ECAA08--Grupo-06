"""Modelos didáticos da Etapa 3 do SCADA do Grupo 06. Sem acesso a hardware.

Algoritmos explícitos, dados locais e resultados reproduzíveis.
As funções não enviam comandos de voo ou de aplicação.
"""
from collections import Counter, deque
from dataclasses import dataclass
from itertools import combinations, count
import heapq
import json
import math
from pathlib import Path
import random
import struct
import zlib

BASE = Path(__file__).resolve().parent
CONFIG = json.loads((BASE / 'cenario.json').read_text(encoding='utf-8'))
PONTOS = {k: tuple(v) for k, v in CONFIG['pontos_m'].items()}
LIMITES = tuple(CONFIG['limites_m'])
OBSTACULOS = [tuple(r) for r in CONFIG['obstaculos_m']]
MARGEM = CONFIG['raio_drone_m'] + CONFIG['folga_m']
EVENTOS = ('INICIO_FAIXA', 'FIM_FAIXA', 'PAUSA', 'RETORNO', 'ALERTA', 'CONCLUSAO')


def inflar(r, margem=MARGEM):
    return (r[0]-margem, r[1]+margem, r[2]-margem, r[3]+margem)


def dentro(p, r):
    return r[0] <= p[0] <= r[1] and r[2] <= p[1] <= r[3]


def intersecta(a, b, r):
    """Slabs: testa todo o segmento fechado, inclusive tangência."""
    lo, hi = 0.0, 1.0
    for eixo, minimo, maximo in [(0, r[0], r[1]), (1, r[2], r[3])]:
        d = b[eixo]-a[eixo]
        if abs(d) < 1e-12:
            if not minimo <= a[eixo] <= maximo:
                return False
        else:
            x, y = sorted(((minimo-a[eixo])/d, (maximo-a[eixo])/d))
            lo, hi = max(lo, x), min(hi, y)
            if lo > hi:
                return False
    return True


def livre(p, obstaculos=OBSTACULOS, margem=MARGEM):
    if len(p) != 2 or not all(math.isfinite(x) for x in p):
        return False
    x0, x1, y0, y1 = LIMITES
    return dentro(p, (x0+margem, x1-margem, y0+margem, y1-margem)) and not any(
        dentro(p, inflar(r, margem)) for r in obstaculos)


def segmento_livre(a, b, obstaculos=OBSTACULOS, margem=MARGEM):
    return livre(a, obstaculos, margem) and livre(b, obstaculos, margem) and not any(
        intersecta(a, b, inflar(r, margem)) for r in obstaculos)


def arestas_mapa():
    return [(a, b, math.dist(PONTOS[a], PONTOS[b])) for a, b in combinations(PONTOS, 2)
            if segmento_livre(PONTOS[a], PONTOS[b])]


def componentes(vertices, arestas):
    adj = {v: set() for v in vertices}
    for u, v, _ in arestas:
        adj[u].add(v); adj[v].add(u)
    faltam = set(vertices); partes = []
    while faltam:
        pilha = [min(faltam)]; vistos = set()
        while pilha:
            v = pilha.pop()
            if v not in vistos:
                vistos.add(v); pilha.extend(adj[v]-vistos)
        faltam -= vistos; partes.append(frozenset(vistos))
    return set(partes)


def validar_grafo(vertices, arestas):
    if len(set(vertices)) != len(vertices):
        raise ValueError('Vértices repetidos')
    vistos = set()
    for u, v, w in arestas:
        e = frozenset((u, v))
        if u not in vertices or v not in vertices or u == v or e in vistos or not math.isfinite(w):
            raise ValueError('Grafo simples inválido')
        vistos.add(e)


def kruskal(vertices, arestas):
    validar_grafo(vertices, arestas)
    pai = {v: v for v in vertices}; tamanho = dict.fromkeys(vertices, 1)
    def raiz(v):
        while pai[v] != v:
            pai[v] = pai[pai[v]]; v = pai[v]
        return v
    arvore, trilha = [], []
    for u, v, w in sorted(arestas, key=lambda e: (e[2], e[0], e[1])):
        a, b = raiz(u), raiz(v); aceita = a != b
        trilha.append((u, v, w, 'ACEITA' if aceita else 'CICLO'))
        if aceita:
            if tamanho[a] < tamanho[b]: a, b = b, a
            pai[b] = a; tamanho[a] += tamanho[b]; arvore.append((u, v, w))
    return arvore, trilha


def prim(vertices, arestas, inicio='BASE'):
    validar_grafo(vertices, arestas)
    adj = {v: [] for v in vertices}
    for u, v, w in arestas:
        adj[u].append((w, u, v)); adj[v].append((w, v, u))
    arvore, trilha, vistos = [], [], set()
    ordem = ([inicio] if inicio in adj else []) + [v for v in vertices if v != inicio]
    for raiz in ordem:
        if raiz in vistos: continue
        vistos.add(raiz); fila = list(adj[raiz]); heapq.heapify(fila)
        while fila:
            w, u, v = heapq.heappop(fila)
            aceita = v not in vistos
            trilha.append((u, v, w, 'ACEITA' if aceita else 'VISITADO'))
            if aceita:
                vistos.add(v); arvore.append((u, v, w))
                for edge in adj[v]: heapq.heappush(fila, edge)
    return arvore, trilha


def custo(arestas):
    return sum(e[2] for e in arestas)


def verificar_floresta(vertices, originais, selecionadas):
    validar_grafo(vertices, selecionadas)
    referencia = {frozenset((u, v)): w for u, v, w in originais}
    assert all(frozenset((u, v)) in referencia and math.isclose(referencia[frozenset((u, v))], w)
               for u, v, w in selecionadas)
    assert componentes(vertices, originais) == componentes(vertices, selecionadas)
    assert len(selecionadas) == len(vertices)-len(componentes(vertices, selecionadas))


def gerar_eventos(faixas=90):
    registros = []; t = 0
    def adicionar(tipo, talhao):
        registros.append(dict(instante_ms=t, id=len(registros)+1, tipo=tipo,
                              missao='SIM_003', talhao=talhao))
    for f in range(faixas):
        talhao = 'T'+str(f % 5+1)
        adicionar(0, talhao); t += 4000
        if (f+1) % 15 == 0:
            adicionar(4, talhao); adicionar(2, talhao); t += 3000
        adicionar(1, talhao); t += 1000
    adicionar(3, 'BASE'); t += 15000; adicionar(5, 'BASE')
    return registros


def huffman(simbolos):
    freq = Counter(simbolos); seq = count(); fila = []
    for s, f in sorted(freq.items()):
        heapq.heappush(fila, (f, next(seq), {'s': s, 'f': f}))
    fusoes = []
    while len(fila) > 1:
        a, _, esq = heapq.heappop(fila); b, _, dire = heapq.heappop(fila)
        fusoes.append((a, b, a+b))
        heapq.heappush(fila, (a+b, next(seq), {'f': a+b, 'esq': esq, 'dir': dire}))
    raiz = fila[0][2] if fila else None
    codigos = {}; pendentes = [(raiz, '')] if raiz else []
    while pendentes:
        no, bits = pendentes.pop()
        if 's' in no: codigos[no['s']] = bits or '0'
        else: pendentes.extend([(no['dir'], bits+'1'), (no['esq'], bits+'0')])
    return raiz, codigos, fusoes


def bits_bytes(bits):
    if not bits: return b''
    bits += '0' * (-len(bits) % 8)
    return bytes(int(bits[i:i+8], 2) for i in range(0, len(bits), 8))


def bytes_bits(data, n):
    if len(data) != (n+7)//8: raise ValueError('Tamanho inconsistente')
    bits = ''.join(f'{b:08b}' for b in data)
    if '1' in bits[n:]: raise ValueError('Padding diferente de zero')
    return bits[:n]


def com_crc(payload):
    return payload + struct.pack('>I', zlib.crc32(payload))


def sem_crc(pacote):
    if len(pacote) < 4: raise ValueError('Pacote truncado')
    data, esperado = pacote[:-4], struct.unpack('>I', pacote[-4:])[0]
    if zlib.crc32(data) != esperado: raise ValueError('CRC inválido')
    return data


def comprimir(simbolos):
    if any(type(s) is not int or s not in range(6) for s in simbolos):
        raise ValueError('Tipo de evento inválido')
    _, codigos, _ = huffman(simbolos)
    bits = ''.join(codigos[s] for s in simbolos)
    dicionario = b''.join(bytes([s, len(c)])+bits_bytes(c) for s, c in sorted(codigos.items()))
    data = struct.pack('>2sIBI', b'HF', len(simbolos), len(codigos), len(bits))
    return com_crc(data+dicionario+bits_bytes(bits))


def descomprimir(pacote):
    data = sem_crc(pacote)
    if len(data) < 11: raise ValueError('Cabeçalho incompleto')
    magic, n, m, nbits = struct.unpack('>2sIBI', data[:11])
    if magic != b'HF' or m > 6: raise ValueError('Cabeçalho inválido')
    pos = 11; codigos = {}; ids = set()
    for _ in range(m):
        if pos+2 > len(data): raise ValueError('Dicionário truncado')
        s, tamanho = data[pos:pos+2]; pos += 2
        if s >= 6 or s in ids or not 1 <= tamanho <= 5: raise ValueError('Código inválido')
        c = bytes_bits(data[pos:pos+(tamanho+7)//8], tamanho); pos += (tamanho+7)//8
        if any(c.startswith(outro) or outro.startswith(c) for outro in codigos):
            raise ValueError('Dicionário não prefixo')
        codigos[c] = s; ids.add(s)
    bits = bytes_bits(data[pos:], nbits); prefixo = ''; resultado = []
    for b in bits:
        prefixo += b
        if prefixo in codigos: resultado.append(codigos[prefixo]); prefixo = ''
        elif not any(c.startswith(prefixo) for c in codigos): raise ValueError('Prefixo inválido')
    if prefixo or len(resultado) != n or (n == 0) != (m == 0):
        raise ValueError('Mensagem incompleta')
    return resultado


def fixo(simbolos):
    if any(type(s) is not int or s not in range(6) for s in simbolos): raise ValueError('Símbolo inválido')
    return com_crc(struct.pack('>2sI', b'FX', len(simbolos))+bits_bytes(''.join(f'{s:03b}' for s in simbolos)))


def ler_fixo(pacote):
    data = sem_crc(pacote)
    if len(data) < 6: raise ValueError('Cabeçalho incompleto')
    magic, n = struct.unpack('>2sI', data[:6])
    if magic != b'FX': raise ValueError('Assinatura inválida')
    bits = bytes_bits(data[6:], 3*n)
    seq = [int(bits[i:i+3], 2) for i in range(0, len(bits), 3)]
    if any(s >= 6 for s in seq): raise ValueError('Símbolo inválido')
    return seq


@dataclass
class NoBST:
    chave: tuple
    evento: dict
    esq: object = None
    dir: object = None


class Historico:
    def __init__(self):
        self.raiz = None; self.ids = set(); self.missao = None

    def inserir(self, evento):
        if type(evento['id']) is not int or type(evento['instante_ms']) is not int:
            raise ValueError('Instante e ID devem ser inteiros')
        if evento['id'] in self.ids or evento['instante_ms'] < 0:
            raise ValueError('Duplicata ou instante negativo')
        if self.missao is not None and evento['missao'] != self.missao:
            raise ValueError('Use um histórico por missão')
        novo = NoBST((evento['instante_ms'], evento['id']), dict(evento)); n = 0
        if self.raiz is None: self.raiz = novo
        else:
            no = self.raiz
            while True:
                n += 1; lado = 'esq' if novo.chave < no.chave else 'dir'
                if getattr(no, lado) is None: setattr(no, lado, novo); break
                no = getattr(no, lado)
        self.ids.add(evento['id']); self.missao = evento['missao']
        return n

    def buscar(self, chave):
        no = self.raiz; visitas = 0
        while no:
            visitas += 1
            if chave == no.chave: return dict(no.evento), visitas
            no = no.esq if chave < no.chave else no.dir
        return None, visitas

    def percurso(self, ordem='em'):
        if ordem not in ('em', 'pre', 'pos'): raise ValueError('Ordem inválida')
        pilha = [(self.raiz, False)]; saida = []
        while pilha:
            no, emitir = pilha.pop()
            if no is None: continue
            if emitir: saida.append(dict(no.evento)); continue
            itens = {'em': [(no.dir, False), (no, True), (no.esq, False)],
                     'pre': [(no.dir, False), (no.esq, False), (no, True)],
                     'pos': [(no, True), (no.dir, False), (no.esq, False)]}
            pilha.extend(itens[ordem])
        return saida

    def intervalo(self, inicio, fim):
        if inicio > fim: raise ValueError('Intervalo invertido')
        no = self.raiz; pilha = []; saida = []
        while no or pilha:
            while no:
                if no.chave[0] < inicio: no = no.dir
                else: pilha.append(no); no = no.esq
            if not pilha: break
            no = pilha.pop()
            if no.chave[0] > fim: break
            saida.append(dict(no.evento)); no = no.dir
        return saida

    def altura(self):
        h = -1; pilha = [(self.raiz, 0)]
        while pilha:
            no, d = pilha.pop()
            if no: h = max(h, d); pilha.extend([(no.esq, d+1), (no.dir, d+1)])
        return h


def ordem_mediana(registros):
    fila = [(0, len(registros))]; saida = []
    while fila:
        a, b = fila.pop()
        if a < b:
            m = (a+b)//2; saida.append(registros[m]); fila.extend([(m+1, b), (a, m)])
    return saida


def rrt(inicio, fim, seed=22, max_iter=2500, passo=10.0, obstaculos=OBSTACULOS):
    if passo <= 0 or not math.isfinite(passo) or type(max_iter) is not int or max_iter < 0:
        raise ValueError('Parâmetros de busca inválidos')
    inicio, fim = tuple(inicio), tuple(fim)
    if not livre(inicio, obstaculos) or not livre(fim, obstaculos):
        return dict(status='PONTO_INVALIDO', nos=[], pais=[], caminho=[], iteracoes=0)
    nos = [inicio]; pais = [None]; rng = random.Random(seed)
    def resultado(status, it, ultimo=None):
        caminho = []
        while ultimo is not None: caminho.append(nos[ultimo]); ultimo = pais[ultimo]
        return dict(status=status, nos=nos, pais=pais, caminho=caminho[::-1], iteracoes=it)
    if inicio == fim: return resultado('SUCESSO', 0, 0)
    x0, x1, y0, y1 = LIMITES
    for it in range(1, max_iter+1):
        alvo = fim if rng.random() < .12 else (rng.uniform(x0+MARGEM, x1-MARGEM), rng.uniform(y0+MARGEM, y1-MARGEM))
        if not livre(alvo, obstaculos): continue
        pai = min(range(len(nos)), key=lambda i: (math.dist(nos[i], alvo), i))
        a = nos[pai]; d = math.dist(a, alvo)
        if d < 1e-12: continue
        b = alvo if d <= passo else tuple(a[k]+passo*(alvo[k]-a[k])/d for k in range(2))
        if not segmento_livre(a, b, obstaculos): continue
        nos.append(b); pais.append(pai)
        if b == fim: return resultado('SUCESSO', it, len(nos)-1)
        if math.dist(b, fim) <= passo and segmento_livre(b, fim, obstaculos):
            pais.append(len(nos)-1); nos.append(fim)
            return resultado('SUCESSO', it, len(nos)-1)
    return resultado('ORCAMENTO_ESGOTADO', max_iter)


def comprimento(caminho):
    return sum(math.dist(a, b) for a, b in zip(caminho, caminho[1:]))


# LAN Ethernet redundante da estação. Nenhum switch é o drone.
BRIDGES = {'SW_SCADA': (4096, '00:00:00:00:00:01'),
           'SW_HMI': (32768, '00:00:00:00:00:02'),
           'SW_RADIO': (32768, '00:00:00:00:00:03')}
LINKS = [('SW_SCADA', 'SW_HMI', 10), ('SW_SCADA', 'SW_RADIO', 10), ('SW_HMI', 'SW_RADIO', 1)]


def spanning_tree(links=LINKS):
    """Seleção centralizada dos papéis estáveis de STP, para LAN ponto a ponto.

    Custos simétricos; sem enlaces paralelos. Não emula troca completa de BPDUs.
    """
    validar_grafo(list(BRIDGES), links)
    if any(w <= 0 for _, _, w in links): raise ValueError('Custo de porta deve ser positivo')
    raiz = min(BRIDGES, key=BRIDGES.get)
    adj = {b: [] for b in BRIDGES}; portas = {}
    for i, (u, v, w) in enumerate(links, 1):
        adj[u].append((v, w, i)); adj[v].append((u, w, i))
        portas[(u, v)] = i; portas[(v, u)] = i
    dist = dict.fromkeys(BRIDGES, math.inf); dist[raiz] = 0; fila = [(0, raiz)]
    while fila:
        d, u = heapq.heappop(fila)
        if d != dist[u]: continue
        for v, w, _ in adj[u]:
            if d+w < dist[v]: dist[v] = d+w; heapq.heappush(fila, (d+w, v))
    if any(math.isinf(d) for d in dist.values()):
        return dict(raiz=raiz, status='PARTICIONADA', custo_raiz=dist, portas=[], ativas=[])
    pais = {}
    for v in BRIDGES:
        if v == raiz: continue
        _, _, _, _, vizinho = min((dist[u]+w, BRIDGES[u], portas[(u, v)], portas[(v, u)], u)
                                  for u, w, _ in adj[v])
        pais[v] = vizinho
    papeis = []; ativas = []
    for u, v, w in links:
        designado = min((u, v), key=lambda b: (dist[b], BRIDGES[b], portas[(b, v if b == u else u)]))
        roles = []
        for a, b in [(u, v), (v, u)]:
            papel = 'ROOT' if pais.get(a) == b else ('DESIGNATED' if a == designado else 'ALTERNATE')
            estado = 'DISCARDING' if papel == 'ALTERNATE' else 'FORWARDING'
            papeis.append((a, b, papel, estado)); roles.append(papel)
        if 'ALTERNATE' not in roles: ativas.append((u, v, w))
    return dict(raiz=raiz, status='CONECTADA', custo_raiz=dist, portas=papeis, ativas=ativas)


def convergencia(protocolo, forward_delay=15.0, atraso_mensagem=.02):
    """Linha do tempo didática após detecção imediata; não é medição de equipamento."""
    if protocolo == 'STP':
        return [(0., 'LISTENING'), (forward_delay, 'LEARNING'), (2*forward_delay, 'FORWARDING')]
    if protocolo == 'RSTP':
        return [(0., 'DISCARDING / PROPOSAL'), (atraso_mensagem, 'SYNC / AGREEMENT'),
                (2*atraso_mensagem, 'FORWARDING')]
    raise ValueError('Protocolo desconhecido')


LUGARES = ('PRONTA', 'DESLOCANDO', 'APLICANDO', 'PAUSADA', 'RETORNANDO', 'CONCLUIDA')
ARCOS = [('iniciar', 0, 1), ('chegar', 1, 2), ('pausar', 2, 3), ('retomar', 3, 2),
         ('finalizar_faixas', 2, 4), ('abortar_pausa', 3, 4), ('abortar_trajeto', 1, 4),
         ('pousar', 4, 5)]


def rede_missao():
    trans = {}
    for nome, origem, destino in ARCOS:
        pre = [0]*6; post = [0]*6; pre[origem] = 1; post[destino] = 1
        trans[nome] = (tuple(pre), tuple(post))
    return trans, (1, 0, 0, 0, 0, 0)


def habilitada(m, pre):
    return all(x >= y for x, y in zip(m, pre))


def disparar(m, transicao):
    pre, post = transicao
    if not habilitada(m, pre): raise ValueError('Transição não habilitada')
    return tuple(x-a+b if not math.isinf(x) else math.inf for x, a, b in zip(m, pre, post))


def atingibilidade(transicoes, inicial, limite=1000):
    vistos = {inicial: 0}; marcas = [inicial]; arcos = []; arvore = []; fila = deque([inicial])
    while fila:
        m = fila.popleft()
        for nome, t in transicoes.items():
            if habilitada(m, t[0]):
                novo = disparar(m, t); repetido = novo in vistos
                if not repetido:
                    if len(marcas) >= limite: raise RuntimeError('Limite de estados: análise incompleta')
                    vistos[novo] = len(marcas); marcas.append(novo); fila.append(novo)
                arcos.append((vistos[m], vistos[novo], nome))
                arvore.append((vistos[m], vistos[novo], nome, repetido))
    return marcas, arcos, arvore


def cobertura(transicoes, inicial, limite=1000):
    """Árvore Karp–Miller clássica para rede P/T, corte só por ancestral igual."""
    nodes = [dict(m=inicial, pai=None, via=None, repetido=False)]; pendentes = [0]
    while pendentes:
        i = pendentes.pop(); m = nodes[i]['m']; ancestrais = []; j = i
        while j is not None: ancestrais.append(nodes[j]['m']); j = nodes[j]['pai']
        if m in ancestrais[1:]: nodes[i]['repetido'] = True; continue
        for nome, t in transicoes.items():
            if not habilitada(m, t[0]): continue
            novo = disparar(m, t)
            # Repetir a aceleração até ponto fixo, usando apenas a cadeia de ancestrais.
            mudou = True
            while mudou:
                anterior = novo
                for a in ancestrais:
                    if all(x >= y for x, y in zip(novo, a)):
                        novo = tuple(math.inf if x > y else x for x, y in zip(novo, a))
                mudou = anterior != novo
            if len(nodes) >= limite: raise RuntimeError('Limite de nós: cobertura incompleta')
            nodes.append(dict(m=novo, pai=i, via=nome, repetido=False)); pendentes.append(len(nodes)-1)
    return nodes


def arvore_atingibilidade(transicoes, inicial):
    """Desdobramento finito da rede limitada: repetições viram folhas referenciadas."""
    nodes=[dict(m=inicial,pai=None,via=None,repetido=False)]
    vistos={inicial}; fila=deque([0])
    while fila:
        i=fila.popleft(); m=nodes[i]['m']
        for nome,t in transicoes.items():
            if habilitada(m,t[0]):
                n=disparar(m,t); repetido=n in vistos
                nodes.append(dict(m=n,pai=i,via=nome,repetido=repetido))
                if not repetido:visto=n;vistos.add(visto);fila.append(len(nodes)-1)
    return nodes


SUCCESS, FAILURE, RUNNING = 'SUCCESS', 'FAILURE', 'RUNNING'


class Folha:
    def __init__(self, nome, func): self.nome = nome; self.func = func
    def tick(self, bb):
        status = self.func(bb); bb['trilha'].append((self.nome, status)); return status


class Composto:
    def __init__(self, nome, filhos, seletor=False):
        self.nome = nome; self.filhos = filhos; self.seletor = seletor
    def tick(self, bb):
        continua = FAILURE if self.seletor else SUCCESS
        for filho in self.filhos:
            estado = filho.tick(bb)
            if estado != continua: bb['trilha'].append((self.nome, estado)); return estado
        final = FAILURE if self.seletor else SUCCESS
        bb['trilha'].append((self.nome, final)); return final


def condicao(nome, predicado):
    return Folha(nome, lambda b: SUCCESS if predicado(b) else FAILURE)


def acao(nome, bomba=False, status=RUNNING):
    def agir(bb): bb['acao'] = nome; bb['bomba_solicitada'] = bomba; return status
    return Folha(nome, agir)


def telemetria(**mudancas):
    t = dict(DRN_LT_01=70., DRN_PT_01=3., DRN_FT_01=2., DRN_ET_01=80., EST_WT_01=3.,
             gps_ok=True, alt_ok=True, comm_ok=True, idade_s=0., e_stop=False,
             auto_mode=True, manual_mode=False, is_flying=True,
             bomba_feedback=True, valvula_feedback=True, estabilizado=True)
    t.update(mudancas); return t


def diagnostico(t):
    """Subconjunto operacional explicitado da continuidade R1–R8, com dados válidos."""
    numericas = {'DRN_LT_01': (0, 100), 'DRN_PT_01': (0, 6), 'DRN_FT_01': (0, 10),
                 'DRN_ET_01': (0, 100), 'EST_WT_01': (0, 25), 'idade_s': (0, math.inf)}
    flags = ['gps_ok', 'alt_ok', 'comm_ok', 'e_stop', 'auto_mode', 'manual_mode',
             'is_flying', 'bomba_feedback', 'valvula_feedback', 'estabilizado']
    validos = all(type(t.get(k)) in (int, float) and math.isfinite(t[k]) and lo <= t[k] <= hi
                  for k, (lo, hi) in numericas.items()) and all(type(t.get(k)) is bool for k in flags)
    if not validos: return ['DADOS_INVALIDOS'], False
    alarmes = []
    if not t['comm_ok'] or t['idade_s'] > 2: alarmes.append('TELEMETRIA_INDISPONIVEL')
    if not t['gps_ok']: alarmes.append('GPS_INVALIDO')
    if t['e_stop']: alarmes.append('EMERGENCIA')
    if not t['alt_ok']: alarmes.append('ALTITUDE_NAO_PERMITIDA')
    if not (t['auto_mode'] and not t['manual_mode']): alarmes.append('MODO_NAO_AUTORIZADO')
    if t['DRN_ET_01'] < 10: alarmes.append('BATERIA_CRITICA')
    if t['DRN_LT_01'] < 5: alarmes.append('NIVEL_CRITICO')
    if t['EST_WT_01'] > 8: alarmes.append('VENTO_ALTO')
    if t['bomba_feedback'] and t['estabilizado'] and t['DRN_FT_01'] < .5:
        if t['valvula_feedback']: alarmes.append('FALHA_PULVERIZACAO')
        if t['DRN_PT_01'] > 5: alarmes.append('POSSIVEL_OBSTRUCAO')
        if t['DRN_PT_01'] < 1: alarmes.append('POSSIVEL_VAZAMENTO_OU_FALHA_BOMBA')
    return alarmes, True


def arvore_comportamento():
    def ramo(nome, p, a): return Composto(nome, [condicao(nome+'?', p), a])
    return Composto('Supervisão reativa', [
        ramo('Emergência', lambda b: b['t'].get('e_stop') is True, acao('EMERGENCIA')),
        ramo('Qualidade', lambda b: not b['dados_ok'], acao('PAUSAR_DADOS')),
        ramo('Bateria crítica', lambda b: 'BATERIA_CRITICA' in b['alarmes'], acao('INTERROMPER_MISSAO')),
        ramo('Bloqueios', lambda b: bool(b['alarmes']) or b['retida'], acao('PAUSAR')),
        ramo('Concluída', lambda b: b.get('concluida', False), acao('CONCLUIR', status=SUCCESS)),
        ramo('Sem aprovação', lambda b: not b.get('aprovada', False), acao('AGUARDAR_OPERADOR')),
        ramo('Retorno', lambda b: b.get('retornar', False) or b['t']['DRN_ET_01'] < 20 or b['t']['DRN_LT_01'] < 20,
             acao('SOLICITAR_RETORNO')),
        ramo('Sem rota', lambda b: not b.get('rota_ok', False), acao('PLANEJAR')),
        ramo('Em deslocamento', lambda b: not b.get('na_faixa', False), acao('DESLOCAR')),
        ramo('Fora de voo', lambda b: not b['t']['is_flying'], acao('AGUARDAR_VOO')),
        acao('PULVERIZAR', bomba=True)
    ], seletor=True)


def tick_supervisor(bb, t):
    bb['t'] = dict(t); bb['trilha'] = []; bb['bomba_solicitada'] = False
    alarmes, validos = diagnostico(t)
    bb['dados_ok'] = validos and t['comm_ok'] and t['idade_s'] <= 2 and t['gps_ok']
    hidraulicos = {'FALHA_PULVERIZACAO', 'POSSIVEL_OBSTRUCAO', 'POSSIVEL_VAZAMENTO_OU_FALHA_BOMBA'}
    bb['retida'] = bb.get('retida', False) or bool(set(alarmes) & hidraulicos)
    if bb.get('rearme') and bb.get('inspecao_confirmada') and validos and not alarmes:
        bb['retida'] = False
    bb['alarmes'] = alarmes
    estado = arvore_comportamento().tick(bb)
    # Barreira final independente da folha escolhida; reiniciada a cada tick.
    permitido = (validos and not alarmes and not bb['retida'] and bb.get('aprovada', False)
                 and bb.get('rota_ok', False) and bb.get('na_faixa', False) and t['is_flying'])
    bb['bomba'] = bool(bb['bomba_solicitada'] and permitido)
    bb['rearme'] = False  # pulso consumido; inspeção sozinha não rearma
    return dict(acao=bb['acao'], status=estado, bomba=bb['bomba'],
                alarmes=alarmes+(['FALHA_RETIDA'] if bb['retida'] else []), trilha=list(bb['trilha']))


@dataclass
class NoKD:
    id: int
    ponto: tuple
    eixo: int
    esq: object = None
    dir: object = None


def kd_construir(pontos, profundidade=0):
    """Recebe pares (ID, ponto); IDs distintos preservam pontos coincidentes."""
    if not pontos: return None
    eixo = profundidade % 2
    ordenados = sorted(pontos, key=lambda x: (x[1][eixo], x[0])); m = len(ordenados)//2
    ident, p = ordenados[m]
    return NoKD(ident, tuple(p), eixo, kd_construir(ordenados[:m], profundidade+1),
                kd_construir(ordenados[m+1:], profundidade+1))


def kd_vizinho(raiz, consulta):
    melhor = (math.inf, math.inf, None); visitas = 0
    def visitar(no):
        nonlocal melhor, visitas
        if no is None: return
        visitas += 1; d2 = sum((a-b)**2 for a, b in zip(no.ponto, consulta))
        candidato = (d2, no.id, no.ponto)
        if candidato[:2] < melhor[:2]: melhor = candidato
        delta = consulta[no.eixo]-no.ponto[no.eixo]
        perto, longe = (no.esq, no.dir) if delta < 0 else (no.dir, no.esq)
        visitar(perto)
        if delta*delta <= melhor[0]: visitar(longe)  # igualdade preserva desempate por ID
    visitar(raiz)
    return (None if melhor[2] is None else (melhor[1], melhor[2], math.sqrt(melhor[0]))), visitas


def kd_raio(raiz, consulta, raio):
    if raio < 0: raise ValueError('Raio negativo')
    resultado = []
    def visitar(no):
        if no is None: return
        if math.dist(no.ponto, consulta) <= raio: resultado.append(no.id)
        delta = consulta[no.eixo]-no.ponto[no.eixo]
        if delta <= raio: visitar(no.esq)
        if delta >= -raio: visitar(no.dir)
    visitar(raiz); return sorted(resultado)


FEATURES = ['DRN_PT_01', 'DRN_FT_01', 'DRN_ET_01', 'EST_WT_01']
CLASSES = ['NORMAL', 'OBSTRUCAO', 'VAZAO_PRESSAO_BAIXAS', 'BATERIA_BAIXA', 'VENTO_ALTO']


def dados_classificacao(seed=27, missoes=30, amostras=30):
    """Dados sintéticos rotulados por cenário injetado, sem observações de campo."""
    rng = random.Random(seed); dados = []
    for m in range(missoes):
        classe = m % len(CLASSES); vies = rng.gauss(0, .10)
        for _ in range(amostras):
            p, q, b, w = rng.gauss(3+vies, .7), rng.gauss(2, .55), rng.uniform(30, 95), rng.uniform(1, 7)
            if classe == 1: p, q = rng.gauss(5.2+vies, .35), rng.uniform(.1, .65)
            if classe == 2: p, q = rng.uniform(.3, 1.2), rng.uniform(.1, .65)
            if classe == 3: b = rng.uniform(5, 24)
            if classe == 4: w = rng.uniform(7.2, 12)
            dados.append({'missao': m, 'x': [max(0, min(6, p)), max(0, q), b, w], 'y': classe})
    return dados


def impureza(labels, criterio='gini'):
    if not labels: return 0.
    probs = [v/len(labels) for v in Counter(labels).values()]
    if criterio == 'gini': return 1-sum(p*p for p in probs)
    if criterio == 'entropy': return -sum(p*math.log2(p) for p in probs)
    raise ValueError('Critério desconhecido')


def treinar_arvore(X, y, criterio='gini', max_depth=4, min_leaf=5, profundidade=0):
    """Árvore binária gulosa para atributos contínuos; não implementa ID3/C4.5."""
    if not X or len(X) != len(y) or min_leaf < 1: raise ValueError('Amostra inválida')
    if any(len(x) != len(X[0]) or not all(math.isfinite(v) for v in x) for x in X):
        raise ValueError('Atributos inválidos')
    cont = Counter(y); classe = min(cont, key=lambda c: (-cont[c], c))
    no = dict(classe=classe, n=len(y), impureza=impureza(y, criterio))
    if profundidade >= max_depth or len(cont) == 1 or len(y) < 2*min_leaf: return no
    melhor = None
    for f in range(len(X[0])):
        valores = sorted(set(x[f] for x in X))
        for a, b in zip(valores, valores[1:]):
            limiar = (a+b)/2
            esquerda = [i for i, x in enumerate(X) if x[f] <= limiar]
            direita = [i for i, x in enumerate(X) if x[f] > limiar]
            if min(len(esquerda), len(direita)) < min_leaf: continue
            perda = sum(len(ix)*impureza([y[i] for i in ix], criterio) for ix in (esquerda, direita))/len(y)
            candidato = (perda, f, limiar, esquerda, direita)
            if melhor is None or candidato[:3] < melhor[:3]: melhor = candidato
    if melhor is None or no['impureza']-melhor[0] <= 1e-12: return no
    _, f, limiar, ie, idr = melhor
    no.update(feature=f, limiar=limiar)
    for lado, ix in [('esq', ie), ('dir', idr)]:
        no[lado] = treinar_arvore([X[i] for i in ix], [y[i] for i in ix], criterio,
                                 max_depth, min_leaf, profundidade+1)
    return no


def prever(no, x):
    if not all(math.isfinite(v) for v in x): raise ValueError('Dado inválido: sem sugestão')
    while 'feature' in no: no = no['esq'] if x[no['feature']] <= no['limiar'] else no['dir']
    return no['classe']


def categorizar(x):
    """Faixas pré-definidas pela engenharia, sem ajuste sobre o conjunto de teste."""
    p,q,b,w=x
    return ('BAIXA' if p < 1 else ('ALTA' if p > 5 else 'NORMAL'),
            'BAIXA' if q < .5 else 'NORMAL', 'BAIXA' if b < 20 else 'NORMAL',
            'ALTO' if w > 8 else 'NORMAL')


def id3(X, y, atributos=None, max_depth=4):
    if not X or len(X)!=len(y): raise ValueError('Amostra inválida')
    atributos=list(range(len(X[0]))) if atributos is None else atributos
    freq=Counter(y); classe=min(freq,key=lambda c:(-freq[c],c))
    no={'classe':classe,'n':len(y)}
    if len(freq)==1 or not atributos or max_depth==0:return no
    escolhas=[]
    for f in atributos:
        partes={v:[i for i,x in enumerate(X) if x[f]==v] for v in sorted({x[f] for x in X})}
        ganho=impureza(y,'entropy')-sum(len(ix)*impureza([y[i] for i in ix],'entropy') for ix in partes.values())/len(y)
        escolhas.append((ganho,-f,partes))
    ganho,neg,partes=max(escolhas,key=lambda a:a[:2]); f=-neg
    if ganho<=1e-12:return no
    no['feature']=f; no['filhos']={}
    for valor,ix in partes.items():
        no['filhos'][valor]=id3([X[i] for i in ix],[y[i] for i in ix],
                               [a for a in atributos if a!=f],max_depth-1)
    return no


def prever_id3(no,x):
    while 'feature' in no:
        valor=x[no['feature']]
        if valor not in no['filhos']:return no['classe']
        no=no['filhos'][valor]
    return no['classe']


def metricas(y, previsto):
    matriz = [[0]*len(CLASSES) for _ in CLASSES]
    for a, b in zip(y, previsto): matriz[a][b] += 1
    f1 = []
    for c in range(len(CLASSES)):
        tp = matriz[c][c]; fp = sum(l[c] for l in matriz)-tp; fn = sum(matriz[c])-tp
        f1.append(2*tp/(2*tp+fp+fn) if 2*tp+fp+fn else 0)
    return dict(acuracia=sum(a == b for a, b in zip(y, previsto))/len(y), macro_f1=sum(f1)/len(f1), confusao=matriz)


def experimento_classificacao():
    dados = dados_classificacao(amostras=20)
    treino = [d for d in dados if d['missao'] % 6 < 4]
    validacao = [d for d in dados if d['missao'] % 6 == 4]
    teste = [d for d in dados if d['missao'] % 6 == 5]
    assert not ({d['missao'] for d in treino} & {d['missao'] for d in teste})
    resultados = []; candidatos = []
    for criterio in ('gini', 'entropy'):
        for profundidade in (2, 3, 4):
            modelo = treinar_arvore([d['x'] for d in treino], [d['y'] for d in treino],
                                    criterio, profundidade, 5)
            met = metricas([d['y'] for d in validacao], [prever(modelo, d['x']) for d in validacao])
            resultados.append(dict(criterio=criterio, profundidade=profundidade, macro_f1_validacao=met['macro_f1']))
            candidatos.append((met['macro_f1'], -profundidade, criterio, modelo))
    _, negativo, criterio, vencedor = max(candidatos, key=lambda c: c[:3])
    # Teste consultado uma única vez após a escolha por validação.
    met = metricas([d['y'] for d in teste], [prever(vencedor, d['x']) for d in teste])
    return dict(dados=dados, modelo=vencedor, grid=resultados, teste=met,
                escolhido=dict(criterio=criterio, profundidade=-negativo),
                grupos={nome: sorted({d['missao'] for d in grupo})
                        for nome, grupo in [('treino', treino), ('validacao', validacao), ('teste', teste)]})


def simular_missao(modelo=None):
    """Replay de doze snapshots e confirmações didáticas de fase, sem dinâmica de voo."""
    agm, _ = kruskal(list(PONTOS), arestas_mapa())
    rota = rrt(PONTOS['BASE'], PONTOS['T1'])
    volta = rrt(PONTOS['T1'], PONTOS['BASE'], seed=28)
    assert rota['status'] == volta['status'] == 'SUCESSO'
    if modelo is None: modelo = experimento_classificacao()['modelo']
    nomes = list(PONTOS); kd = kd_construir(list(enumerate(PONTOS.values())))
    rede, marcacao = rede_missao(); alcancaveis = set(atingibilidade(rede, marcacao)[0])
    bb = dict(aprovada=False, rota_ok=True, na_faixa=False)
    cenario = [
        ('Pré-missão: aguarda aprovação', {}, {}),
        ('Aprovação e deslocamento', {'aprovada': True}, {}),
        ('Entrada na faixa confirmada', {'na_faixa': True}, {}),
        ('Vento acima do limite', {}, {'EST_WT_01': 9.}),
        ('Vento normalizado', {}, {}),
        ('Indício de obstrução', {}, {'DRN_PT_01': 5.6, 'DRN_FT_01': .2}),
        ('Bomba parada; falha retida', {}, {'bomba_feedback': False, 'DRN_FT_01': 0.}),
        ('Inspeção e rearme confirmados', {'rearme': True, 'inspecao_confirmada': True}, {}),
        ('Falha do enlace da LAN', {}, {'comm_ok': False, 'idade_s': 3.}),
        ('Rede e telemetria recuperadas', {}, {}),
        ('Bateria baixa: retorno solicitado', {}, {'DRN_ET_01': 15.}),
        ('Pouso confirmado pelo simulador', {'concluida': True}, {'is_flying': False, 'bomba_feedback': False, 'DRN_ET_01': 15.})
    ]
    linhas = []; eventos = []; historico = Historico(); redes = []
    for k, (descricao, mudancas, sensores) in enumerate(cenario):
        bb.update(mudancas); t = telemetria(**sensores)
        links = LINKS if k < 8 else [e for e in LINKS if set(e[:2]) != {'SW_SCADA', 'SW_RADIO'}]
        lan = spanning_tree(links); redes.append(lan)
        # Em k=8 a pausa representa a janela de reconvergência modelada.
        res = tick_supervisor(bb, t); a = res['acao']; estado = LUGARES[marcacao.index(1)]
        transicao = None
        if a == 'DESLOCAR' and estado == 'PRONTA': transicao = 'iniciar'
        elif a == 'PULVERIZAR':
            if estado == 'DESLOCANDO': transicao = 'chegar'
            elif estado == 'PAUSADA': transicao = 'retomar'
        elif a.startswith('PAUSAR') and estado == 'APLICANDO': transicao = 'pausar'
        elif a == 'SOLICITAR_RETORNO':
            assert volta['status'] == 'SUCESSO'
            transicao = {'APLICANDO': 'finalizar_faixas', 'PAUSADA': 'abortar_pausa',
                         'DESLOCANDO': 'abortar_trajeto'}.get(estado)
        elif a == 'CONCLUIR' and estado == 'RETORNANDO': transicao = 'pousar'
        if transicao: marcacao = disparar(marcacao, rede[transicao])
        assert marcacao in alcancaveis and sum(marcacao) == 1
        assert not res['bomba'] or marcacao[2] == 1
        tipo = 0 if a == 'PULVERIZAR' else (3 if a == 'SOLICITAR_RETORNO' else (5 if a == 'CONCLUIR' else 2))
        tipos = ([4] if res['alarmes'] else [])+[tipo]
        for tipo in tipos:
            e = dict(instante_ms=k*1000, id=len(eventos)+1, tipo=tipo, missao='SIM_028', talhao='T1')
            eventos.append(e); historico.inserir(e)
        pos = PONTOS['BASE'] if k < 2 or k == 11 else PONTOS['T1']
        vizinho, _ = kd_vizinho(kd, pos)
        sugestao = CLASSES[prever(modelo, [t[f] for f in FEATURES])] if bb['dados_ok'] else 'INDISPONIVEL'
        linhas.append(dict(tick=k, descricao=descricao, acao=a, estado_petri=LUGARES[marcacao.index(1)],
                           bomba=res['bomba'], alarmes='; '.join(res['alarmes']) or 'SEM_ALARME',
                           sugestao_ml=sugestao, ponto_proximo=nomes[vizinho[0]],
                           pressao=t['DRN_PT_01'], vazao=t['DRN_FT_01'], bateria=t['DRN_ET_01'],
                           nivel=t['DRN_LT_01'], vento=t['EST_WT_01'], transicao=transicao or '—'))
    seq = [e['tipo'] for e in eventos]; pacote = comprimir(seq)
    assert descomprimir(pacote) == seq
    assert historico.percurso() == sorted(eventos, key=lambda e: (e['instante_ms'], e['id']))
    return dict(linhas=linhas, eventos=eventos, agm=agm, rota=rota, volta=volta,
                redes=redes, huffman_bytes=len(pacote), fixo_bytes=len(fixo(seq)))
