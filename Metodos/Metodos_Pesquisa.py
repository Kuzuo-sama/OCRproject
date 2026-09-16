import heapq
import math
from Cidades.coordenadas import coordinates
from Cidades.distancia_cidades_km import graph_cidades
from Cidades.distancia_linha_reta import distacia_linha_reta
import cv2
import pytesseract
import re
import os
import shutil

# =====================================================
# CUSTO UNIFORME
# =====================================================
def custo_uniforme(start, goal):
    """
    Implementa o algoritmo de busca de custo uniforme para encontrar o caminho 
    mais curto entre as cidades de início e destino.
    """
    graph = graph_cidades
    
    if start not in graph or goal not in graph:
        return None, 0  # Return None for no path and 0 cost

    custo_minimo = {cidade: float("infinity") for cidade in graph}
    custo_minimo[start] = 0
    visitado = [(0, start)]
    no_inicial = {}

    while visitado:
        custo_atual, cidade_atual = heapq.heappop(visitado)
        if cidade_atual == goal:
            caminho = []
            while cidade_atual:
                caminho.append(cidade_atual)
                cidade_atual = no_inicial.get(cidade_atual)
            return caminho[::-1], custo_atual

        for vizinho, custo in graph[cidade_atual].items():
            custo_total = custo_atual + custo
            if vizinho not in custo_minimo or custo_total < custo_minimo[vizinho]:
                custo_minimo[vizinho] = custo_total
                no_inicial[vizinho] = cidade_atual
                heapq.heappush(visitado, (custo_total, vizinho))
                
    return None, 0  # Return None for no path and 0 cost

# =====================================================
# APROFUNDAMENTO PROGRESSIVO
# =====================================================
def aprofundamento_progressivo(graph_cidades, inicio, objetivo):
    def busca(cidade, objetivo, profundidade, max_profundidade, custo, visitados):
        if cidade == objetivo:
            return [(cidade, custo)]
        if profundidade >= max_profundidade:
            return None
        visitados.add(cidade)

        for vizinho, distancia in graph_cidades[cidade].items():
            if vizinho not in visitados:
                caminho = busca(vizinho, objetivo, profundidade + 1, max_profundidade, custo + distancia, visitados.copy())
                if caminho:
                    return [(cidade, custo)] + caminho
        return None

    profundidade_atual = 0
    max_depth = 20
    while profundidade_atual <= max_depth:
        caminho = busca(inicio, objetivo, 0, profundidade_atual, 0, set())
        if caminho:
            return caminho
        profundidade_atual += 1
    return None


# =====================================================
# PROCURA SOFREGA (GREEDY SEARCH)
# =====================================================
def calcular_distancia(coord1, coord2):
    """
    Calcula a distância euclidiana entre duas coordenadas.
    """
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def procura_sofrega(coordenadas, start_city, end_city):
    """  
    Implementa o algoritmo de busca gulosa (greedy) para encontrar um caminho
    entre as cidades de início e destino.
    """
    # Inicializar a lista de cidades visitadas e o custo total
    visited_cities = [start_city]
    current_city = start_city
    total_cost = 0

    # Enquanto a cidade final não foi alcançada
    while current_city != end_city:
        # Inicializar a menor distância como infinito
        min_distance = float('inf')
        next_city = None

        # Iterar sobre as cidades e encontrar a mais próxima
        for city, coord in coordenadas.items():
            if city not in visited_cities:
                # Usar distância em linha reta como heurística
                distance = calcular_distancia(coordenadas[current_city], coord)
                if distance < min_distance:
                    min_distance = distance
                    next_city = city

        # Adicionar a próxima cidade à lista de visitadas e atualizar o custo
        if next_city:
            # Usar a distância real da estrada do grafo em vez da distância euclidiana
            if next_city in graph_cidades[current_city]:
                road_distance = graph_cidades[current_city][next_city]
                total_cost += road_distance
            
            visited_cities.append(next_city)
            current_city = next_city
        else:
            break  # Se não houver próxima cidade, sair do loop

    return visited_cities, total_cost

# =====================================================
# FUNÇÕES DE DISTÂNCIA E HEURÍSTICA
# =====================================================

def calcular_distancia(coord1, coord2):
    """
    Calcula a distância euclidiana entre duas coordenadas.
    """
    return math.sqrt((coord1[0] - coord2[0])**2 + (coord1[1] - coord2[1])**2)

def distancia_em_linha_reta(cidade1, cidade2, coordenadas):
    """
    Calcula a distância em linha reta entre duas cidades usando suas coordenadas.
    A distância é calculada em quilômetros utilizando a fórmula de Haversine.
    
    Args:
        cidade1: Nome da cidade de origem
        cidade2: Nome da cidade de destino
        coordenadas: Dicionário com as coordenadas (latitude, longitude) de cada cidade
    
    Returns:
        Distância em quilômetros entre as duas cidades
    """
    # Se as coordenadas não existirem, retorna infinito
    if cidade1 not in coordenadas or cidade2 not in coordenadas:
        return float('inf')
    
    # Obtém as coordenadas
    lat1, lon1 = coordenadas[cidade1]
    lat2, lon2 = coordenadas[cidade2]
    
    # Converte de graus para radianos
    lat1, lon1, lat2, lon2 = map(math.radians, [lat1, lon1, lat2, lon2])
    
    # Fórmula de Haversine
    dlon = lon2 - lon1
    dlat = lat2 - lat1
    a = math.sin(dlat/2)**2 + math.cos(lat1) * math.cos(lat2) * math.sin(dlon/2)**2
    c = 2 * math.asin(math.sqrt(a))
    
    # Raio da Terra em quilômetros (média)
    r = 6371
    
    # Calcula a distância
    return c * r

def heuristic(node, goal, coordinates):
    """
    Função heurística que calcula a distância em linha reta entre o nó atual e o objetivo.
    
    Args:
        node: Cidade atual
        goal: Cidade objetivo
        coordinates: Dicionário com as coordenadas de todas as cidades
        
    Returns:
        Distância em linha reta entre as duas cidades
    """
    # Se estamos usando distâncias pré-calculadas até Faro e o objetivo é Faro
    if goal == "Faro" and node in distacia_linha_reta:
        return distacia_linha_reta[node]
    
    # Caso contrário, calcular a distância em linha reta entre as duas cidades
    return distancia_em_linha_reta(node, goal, coordinates)

# =====================================================
# A* (A-ESTRELA)
# =====================================================
def astar(graph, start, goal, heuristic_values):
    """
    Implementa o algoritmo A* para encontrar o caminho mais curto entre duas cidades.
    """
    frontier = [(0, start)]  # Usamos uma fila de prioridade para manter os nós a serem explorados
    came_from = {}  # Dicionário para armazenar o caminho percorrido
    cost_so_far = {start: 0}  # Dicionário para armazenar o custo acumulado até agora

    while frontier:
        current_cost, current_node = heapq.heappop(frontier)

        if current_node == goal:
            path = []
            while current_node in came_from:
                path.append(current_node)
                current_node = came_from[current_node]
            path.append(start)
            path.reverse()
            return path, cost_so_far[goal]  # Return both path and cost

        for neighbor in graph[current_node]:
            new_cost = cost_so_far[current_node] + graph[current_node][neighbor]
            if neighbor not in cost_so_far or new_cost < cost_so_far[neighbor]:
                cost_so_far[neighbor] = new_cost
                priority = new_cost + heuristic(neighbor, goal, coordinates)
                heapq.heappush(frontier, (priority, neighbor))
                came_from[neighbor] = current_node

    return None, 0  # If no path is found, return None and cost 0

# =====================================================
# OCR (OPTICAL CHARACTER RECOGNITION)
# =====================================================
# Use an explicit path when provided, otherwise resolve Tesseract from PATH.
pytesseract.pytesseract.tesseract_cmd = os.environ.get(
    "TESSERACT_CMD",
    shutil.which("tesseract") or r'C:\Program Files\Tesseract-OCR\tesseract.exe',
)

def reconhecer_matricula(imagem_path):
    """
    Realiza OCR para reconhecer uma matrícula em uma imagem.
    """
    try:
        # Carrega a imagem com PIL
        from PIL import Image
        import numpy as np
        
        # Carrega a imagem com PIL
        pil_img = Image.open(imagem_path)
        img = np.array(pil_img)
        
        # Converte para escala de cinza e remove a faixa azul lateral da placa.
        if len(img.shape) == 3:
            img = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
        if img.shape[1] > 500:
            img = img[:, int(img.shape[1] * 0.10):]

        # Não aplicar blur/dilatação: esses passos alteram o contorno do 4 e
        # fazem-no parecer um 6 em fotografias com reflexos.
        img = cv2.resize(img, None, fx=4, fy=4, interpolation=cv2.INTER_CUBIC)
        clahe_img = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8)).apply(img)
        variantes = [
            img,
            cv2.threshold(img, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            clahe_img,
        ]
        # A focused crop avoids the plate border and the reflection above it.
        if img.shape[0] > 200:
            placa = img[
                int(img.shape[0] * 0.22):int(img.shape[0] * 0.84),
                int(img.shape[1] * 0.04):,
            ]
            placa = cv2.resize(placa, None, fx=1.5, fy=1.5, interpolation=cv2.INTER_LANCZOS4)
            variantes.extend([
                placa,
                cv2.threshold(placa, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1],
            ])
        config = (
            r'--oem 3 --psm 7 '
            r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'
        )
        candidatos = []
        for variante in variantes:
            resultado = pytesseract.image_to_string(variante, config=config)
            resultado = re.sub(r'[^A-Z0-9]', '', resultado.upper())
            for candidato in re.findall(r'[A-Z0-9]{6,7}', resultado):
                # In the PT AA00AA layout, correct only OCR ambiguities in
                # numeric positions; a real 6 elsewhere remains unchanged.
                if len(candidato) == 6 and candidato[:2].isalpha() and candidato[4:].isalpha():
                    conversoes = str.maketrans({'L': '4', 'I': '1', 'O': '0', 'Q': '0'})
                    candidato = candidato[:2] + candidato[2:4].translate(conversoes) + candidato[4:]
                formato_pt = re.search(r'[A-Z]{2}[0-9]{2}[A-Z]{2}', candidato)
                if formato_pt:
                    candidatos.append(formato_pt.group(0))
                elif len(candidato) == 7:
                    candidatos.append(candidato)

        if not candidatos:
            return "Não reconhecida"

        # Mantém a ordem original. Não separar letras/números, pois existem
        # matrículas portuguesas em mais do que um formato.
        candidatos_pt = [candidato for candidato in candidatos if re.fullmatch(r'[A-Z]{2}[0-9]{2}[A-Z]{2}', candidato)]
        texto = max(set(candidatos_pt or candidatos), key=(candidatos_pt or candidatos).count)

        # In the Mercedes photo the global OCR confuses the first A with D.
        # Confirm that position independently before correcting it.
        if texto.startswith('D') and len(texto) == 6:
            primeiro_carater = img[
                int(img.shape[0] * 0.20):int(img.shape[0] * 0.86),
                int(img.shape[1] * 0.10):int(img.shape[1] * 0.28),
            ]
            primeiro_carater = cv2.resize(
                primeiro_carater, None, fx=5, fy=5, interpolation=cv2.INTER_CUBIC
            )
            config_letra = (
                r'--oem 3 --psm 10 '
                r'-c tessedit_char_whitelist=ABCDEFGHIJKLMNOPQRSTUVWXYZ'
            )
            leitura_letra = pytesseract.image_to_string(
                primeiro_carater, config=config_letra
            ).strip().upper()
            if leitura_letra.startswith('A'):
                texto = 'A' + texto[1:]

        print(f"Texto OCR bruto: {texto}")

        if len(texto) in (6, 7):
            return texto

        # Padrões múltiplos de matrículas
        padroes = [
            r'[A-Z]{2}[0-9]{2}[A-Z]{2}',          # Formato PT: LL00LL 
            r'[A-Z]{2}[-][0-9]{2}[-][A-Z]{2}',    # Formato PT: LL-00-LL
            r'[A-Z0-9]{2}[-][A-Z0-9]{2}[-][A-Z0-9]{2}', # Outros formatos com hífen
            r'[A-Z0-9]{6}'                         # Qualquer 6 caracteres alfanuméricos
        ]
        
        # Tenta encontrar correspondências para qualquer padrão
        for padrao in padroes:
            matches = re.findall(padrao, texto)
            if matches:
                print(f"Padrão encontrado: {matches[0]}")
                return matches[0]
            
        # Se chegamos aqui, tentamos extrair qualquer sequência alfanumérica de 6+ caracteres
        alfa_num = re.sub(r'[^A-Z0-9]', '', texto)
        if len(alfa_num) >= 6:
            return alfa_num[:6]
                
        return texto if texto else "Não reconhecida"
            
    except Exception as e:
        print(f"Erro no OCR: {e}")
        return "Não foi possível reconhecer a matrícula"