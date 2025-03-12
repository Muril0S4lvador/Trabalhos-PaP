import pandas as pd
from SPARQLWrapper import SPARQLWrapper, JSON
from itertools import combinations
from functools import reduce

# Configuração do endpoint da DBpedia
sparql = SPARQLWrapper("https://dbpedia.org/sparql")
query = """
    PREFIX dbp: <http://dbpedia.org/property/>
    PREFIX db: <http://dbpedia.org/>
    PREFIX rdfs: <http://www.w3.org/2000/01/rdf-schema#>
    PREFIX dbo: <http://dbpedia.org/ontology/>

    SELECT DISTINCT ?anoInicio ?anoFim ?modelo ?nomeMarca ?nomeCategoria
    WHERE {
        ?c a dbo:Automobile;
           dbo:manufacturer ?marca;
           dbo:bodyStyle ?categoria;
           dbo:productionStartYear ?anoInicio;
           dbo:productionEndYear ?anoFim.

        OPTIONAL { ?c rdfs:label ?modeloEn FILTER(lang(?modeloEn) = 'en') }
        OPTIONAL { ?c rdfs:label ?modeloPt FILTER(lang(?modeloPt) = 'pt') }
        BIND(COALESCE(?modeloEn, ?modeloPt) AS ?modelo)

        OPTIONAL { ?marca rdfs:label ?marcaEn FILTER(lang(?marcaEn) = 'en') }
        OPTIONAL { ?marca rdfs:label ?marcaPt FILTER(lang(?marcaPt) = 'pt') }
        BIND(COALESCE(?marcaEn, ?marcaPt) AS ?nomeMarca)

        OPTIONAL { ?categoria rdfs:label ?categoriaEn FILTER(lang(?categoriaEn) = 'en') }
        OPTIONAL { ?categoria rdfs:label ?categoriaPt FILTER(lang(?categoriaPt) = 'pt') }
        BIND(COALESCE(?categoriaEn, ?categoriaPt) AS ?nomeCategoria)
    }
"""

sparql.setQuery(query)
sparql.setReturnFormat(JSON)
results = sparql.query().convert()

# Transformando os resultados em um DataFrame
data = []
for result in results["results"]["bindings"]:
    data.append({
        "Inicio": result.get("anoInicio", {}).get("value", None),
        "Fim": result.get("anoFim", {}).get("value", None),
        "Modelo": result.get("modelo", {}).get("value", None),
        "Marca": result.get("nomeMarca", {}).get("value", None),
        "Categoria": result.get("nomeCategoria", {}).get("value", None),
    })

df = pd.DataFrame(data)
df.head()

carros = df[["Modelo", "Marca", "Categoria", "Inicio", "Fim"]].dropna().to_dict(orient="records")

############################################################################################
################################ Regra 1 ###################################################
############################################################################################
# Carros são concorrentes se as marcas forem diferentes e as categorias forem as mesmas
def concorrentes(Modelo1=None, Modelo2=None):
    pares = list(combinations(carros, 2))

    concorrentes = list(filter(lambda p: p[0]["Marca"] != p[1]["Marca"] and p[0]["Categoria"] == p[1]["Categoria"], pares))

    if not Modelo1 and not Modelo2:
        # Caso ambos sejam vazios, retorna todos os concorrentes
        for c1, c2 in concorrentes:
            print(c1["Modelo"], "-", c2["Modelo"])
    elif Modelo1 and not Modelo2:
        # Caso apenas um modelo seja passado, retorna seus concorrentes
        modelos_concorrentes = list(filter(lambda p: p[0]["Modelo"] == Modelo1 or p[1]["Modelo"] == Modelo1, concorrentes))
        for c1, c2 in modelos_concorrentes:
            print(c1["Modelo"], "-", c2["Modelo"])
    elif Modelo1 and Modelo2:
        # Caso os dois modelos sejam passados, retorna True ou False
        return any((p[0]["Modelo"] == Modelo1 and p[1]["Modelo"] == Modelo2) or 
                   (p[0]["Modelo"] == Modelo2 and p[1]["Modelo"] == Modelo1) for p in concorrentes)
    
############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# concorrentes()
# concorrentes("Mitsubishi Dignity")
# concorrentes("Mitsubishi Dignity", "Cadillac DTS")
# concorrentes("Cadillac DTS", "BYD M6")

############################################################################################
################################ Regra 2 ###################################################
############################################################################################
# Carros de luxo se são de determinada marca ou categorias
def carro_de_luxo(Modelo=None):
    criterios = ["Rolls-Royce", "Sport", "Convertible", "Limousine"]
    
    carros_luxo = list(filter(lambda c: any(criterio in (c["Marca"] or "") or criterio in (c["Categoria"] or "") for criterio in criterios), carros))
    
    if not Modelo:
        for c in carros_luxo:
            print(c["Modelo"])
    else:
        return any(c["Modelo"] == Modelo for c in carros_luxo)
    
############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# carro_de_luxo()
# carro_de_luxo("BYD M6")
# carro_de_luxo("Cadillac DTS")

############################################################################################
################################ Regra 3 ###################################################
############################################################################################
# Encontrar carros que iniciem com uma letra Letra
def encontrar_carros_com_letra(Letra=None, Lista=None):
    carros_filtrados = list(filter(lambda c: c["Modelo"].startswith(Letra), carros)) if Letra else carros
    
    if Lista is None:
        for c in carros_filtrados:
            print((c["Modelo"], c["Marca"]))
    else:
        carros_tuplas = list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))
        
        return reduce(lambda acc, x: acc and (x in carros_tuplas), Lista, True)

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# encontrar_carros_com_letra()
# encontrar_carros_com_letra("X")
# encontrar_carros_com_letra("X", [("Xiali N7","FAW Group"), ("Xiali N5","FAW Group")])
# encontrar_carros_com_letra("Z", [("Xiali N7","FAW Group"), ("Xiali N5","FAW Group")])

############################################################################################
################################ Regra 4 ###################################################
############################################################################################
# Encontrar carros que pertencem a uma determinada Marca
def encontrar_carros_de_marca(Marca=None, Lista=None):
    carros_filtrados = list(filter(lambda c: c["Marca"] == Marca, carros)) if Marca else carros
    
    if Lista is None:
        for c in carros_filtrados:
            print((c["Modelo"], c["Marca"]))
    else:
        carros_tuplas = list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))
        
        return reduce(lambda acc, x: acc and (x in carros_tuplas), Lista, True)
    
############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# encontrar_carros_de_marca()
# encontrar_carros_de_marca("ZiL")
# encontrar_carros_de_marca("ZiL", [("ZIL-118","ZiL"), ("ZIL-4102","ZiL"), ("ZIL-4102","ZiL")])
# encontrar_carros_de_marca("Fiat", [("ZIL-118","ZiL"), ("ZIL-4102","ZiL"), ("ZIL-4102","ZiL")])

############################################################################################
################################ Regra 5 ###################################################
############################################################################################
# Quantidade de carros que pertencem a uma determinada Marca
def carros_por_marca(Marca=None):
    quantidade = reduce(lambda acc, c: acc + 1 if (not Marca or c["Marca"] == Marca) else acc, carros, 0)
    
    print(f'Total de carros da marca {Marca}: {quantidade}' if Marca else f'Total de carros: {quantidade}')

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# carros_por_marca()
# carros_por_marca("Fiat")
# carros_por_marca("ZiL")

############################################################################################
################################ Regra 6 ###################################################
############################################################################################
# Regra para encontrar o modelo mais antigo de uma marca ou de todos
def modelo_mais_antigo(Marca=None):
    carros_validos = list(filter(lambda c: c.get("Inicio") and c["Inicio"].isdigit() and int(c["Inicio"]) > 1800 and (Marca is None or c["Marca"] == Marca), carros))
    
    if not carros_validos:
        print("Nenhum carro encontrado com os critérios informados.")
        return
    
    carro_mais_antigo = sorted(carros_validos, key=lambda c: int(c["Inicio"]))[0]
    
    ano_atual = 2025
    idade = ano_atual - int(carro_mais_antigo["Inicio"])
    
    print(f'Modelo: {carro_mais_antigo["Modelo"]}')
    print(f'Marca: {carro_mais_antigo["Marca"]}')
    print(f'Ano Início Fabricação: {carro_mais_antigo["Inicio"]}')
    print(f'Idade do Modelo: {idade} anos')

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# modelo_mais_antigo()
# modelo_mais_antigo("Fiat")
# modelo_mais_antigo("Volkswagen")

############################################################################################
################################ Regra 7 ###################################################
############################################################################################
# Pega todos os modelos que não pagam mais IPVA no Brasil por marca
def modelo_livre_de_ipva_por_marca(Marca=None, Lista=None):
    ano_atual = 2025
    ano_limite = ano_atual - 15
    
    carros_isentos = list(filter(lambda c: c.get("Fim") and c["Fim"].isdigit() and int(c["Fim"]) < ano_limite and (Marca is None or c["Marca"] == Marca), carros))
    
    if Lista is None:
        list(map(lambda c: print((c["Modelo"], c["Marca"])), carros_isentos))
    else:
        carros_tuplas = list(map(lambda c: (c["Modelo"], c["Marca"]), carros_isentos))
        
        return reduce(lambda acc, x: acc and (x in carros_tuplas), Lista, True)

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# modelo_livre_de_ipva_por_marca()
# modelo_livre_de_ipva_por_marca("Fiat")
# modelo_livre_de_ipva_por_marca("ZiL", [('ZIL-4102', 'ZiL'), ('ZIL-118', 'ZiL'), ('ZIL-4102', 'ZiL')])
# modelo_livre_de_ipva_por_marca("Trabant", [("RGW-Auto","Trabant",1972), ("RGW-Auto","Trabant",1972), ("RGW-Auto","Trabant",1972)])

############################################################################################
################################ Regra 8 ###################################################
############################################################################################
# Informa se uma marca possui ou não pelo menos um carro de luxo. Corte limita a busca a uma aparição true
def possui_carros_de_luxo(Marca=None):
    categorias_luxo = ["Rolls-Royce", "Sport", "Convertible", "Limousine"]
    
    if Marca:
        return any(c["Marca"] == Marca and any(cat in c["Categoria"] for cat in categorias_luxo) for c in carros)
    else:
        marcas_luxo = set(map(lambda c: c["Marca"], filter(lambda c: any(cat in c["Categoria"] for cat in categorias_luxo), carros)))
        print("Marcas com carros de luxo:", list(marcas_luxo))

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# possui_carros_de_luxo()
# possui_carros_de_luxo("Trabant")
# possui_carros_de_luxo("SEAT")
