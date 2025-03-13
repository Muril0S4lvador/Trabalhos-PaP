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
    return (
        (lambda concorrentes: 
            (lambda: 
                list(map(lambda p: f"{p[0]['Modelo']} - {p[1]['Modelo']}", concorrentes))
                if not Modelo1 and not Modelo2 else
                (lambda modelos_concorrentes: 
                    list(map(lambda p: f"{p[0]['Modelo']} - {p[1]['Modelo']}", modelos_concorrentes))
                    if Modelo1 and not Modelo2 else
                    any((p[0]["Modelo"] == Modelo1 and p[1]["Modelo"] == Modelo2) or
                         (p[0]["Modelo"] == Modelo2 and p[1]["Modelo"] == Modelo1) for p in concorrentes)
                )(list(filter(lambda p: p[0]["Modelo"] == Modelo1 or p[1]["Modelo"] == Modelo1, concorrentes)))
            )() if not Modelo1 or not Modelo2 else
            any((p[0]["Modelo"] == Modelo1 and p[1]["Modelo"] == Modelo2) or
                 (p[0]["Modelo"] == Modelo2 and p[1]["Modelo"] == Modelo1) for p in concorrentes)
        )(list(filter(lambda p: p[0]["Marca"] != p[1]["Marca"] and p[0]["Categoria"] == p[1]["Categoria"], combinations(carros, 2)))))
    
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
    return (
        (lambda carros_luxo: 
            (lambda: 
                list(map(lambda c: c["Modelo"], carros_luxo))
                if not Modelo else
                any(c["Modelo"] == Modelo for c in carros_luxo)
            )()
        )(list(filter(lambda c: any(criterio in (c["Marca"] or "") or criterio in (c["Categoria"] or "") for criterio in ["Rolls-Royce", "Sport", "Convertible", "Limousine"]), carros)))
    )
    
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
    return (
        (lambda carros_filtrados: 
            (lambda: 
                list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))
                if Lista else
                list(map(lambda c: print((c["Modelo"], c["Marca"])), carros_filtrados))
            )()
        )(list(filter(lambda c: c["Modelo"].startswith(Letra) if Letra else True, carros)))
        if Lista else
        reduce(lambda acc, x: acc and (x in list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))), Lista, True)
    )

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
    return (
        (lambda carros_filtrados:
            (lambda: 
                list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))
                if Lista else
                list(map(lambda c: print((c["Modelo"], c["Marca"])), carros_filtrados))
            )()
        )(list(filter(lambda c: c["Marca"] == Marca if Marca else True, carros)))
        if Lista else
        reduce(lambda acc, x: acc and (x in list(map(lambda c: (c["Modelo"], c["Marca"]), carros_filtrados))), Lista, True)
    )
    
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
    return (
        (lambda quantidade: 
            print(f'Total de carros da marca {Marca}: {quantidade}' if Marca else f'Total de carros: {quantidade}')
        )(
            reduce(lambda acc, c: acc + 1 if (not Marca or c["Marca"] == Marca) else acc, carros, 0)
        )
    )

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
    return (
        (lambda carros_validos:
            (lambda: 
                (lambda carro_mais_antigo:
                    (lambda idade: 
                        (print(f'Modelo: {carro_mais_antigo["Modelo"]}'),
                         print(f'Marca: {carro_mais_antigo["Marca"]}'),
                         print(f'Ano Início Fabricação: {carro_mais_antigo["Inicio"]}'),
                         print(f'Idade do Modelo: {idade} anos'))
                    )(2025 - int(carro_mais_antigo["Inicio"]))
                )(sorted(carros_validos, key=lambda c: int(c["Inicio"]))[0])
            )()
        )(
            list(filter(lambda c: c.get("Inicio") and c["Inicio"].isdigit() and int(c["Inicio"]) > 1800 and (Marca is None or c["Marca"] == Marca), carros))
        ) if list(filter(lambda c: c.get("Inicio") and c["Inicio"].isdigit() and int(c["Inicio"]) > 1800 and (Marca is None or c["Marca"] == Marca), carros)) else print("Nenhum carro encontrado com os critérios informados.")
    )

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
    return (
        (lambda carros_isentos:
            (lambda: 
                list(map(lambda c: print((c["Modelo"], c["Marca"])), carros_isentos))
                if Lista is None else
                reduce(lambda acc, x: acc and (x in list(map(lambda c: (c["Modelo"], c["Marca"]), carros_isentos))), Lista, True)
            )()
        )(
            list(filter(lambda c: c.get("Fim") and c["Fim"].isdigit() and int(c["Fim"]) < 2025 - 15 and (Marca is None or c["Marca"] == Marca), carros))
        )
    )

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
    return (
        (lambda: 
            any(c["Marca"] == Marca and any(cat in c["Categoria"] for cat in ["Rolls-Royce", "Sport", "Convertible", "Limousine"]) for c in carros)
            if Marca else
            (lambda marcas_luxo: print("Marcas com carros de luxo:", list(marcas_luxo)))(set(map(lambda c: c["Marca"], filter(lambda c: any(cat in c["Categoria"] for cat in ["Rolls-Royce", "Sport", "Convertible", "Limousine"]), carros))))
        )()
    )

############################################################################################
######################## EXEMPLOS DE CONSULTAS #############################################
############################################################################################

# possui_carros_de_luxo()
# possui_carros_de_luxo("Trabant")
# possui_carros_de_luxo("SEAT")
