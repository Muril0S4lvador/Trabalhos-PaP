:- data_source(
  dbpedia_carros,
  sparql("
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
}",[endpoint('https://dbpedia.org/sparql')])).


carros(Inicio, Fim, Modelo, Marca, Categoria) :-
    dbpedia_carros{anoInicio:Inicio, anoFim:Fim, modelo:Modelo, nomeMarca:Marca, nomeCategoria:Categoria}.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 1 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Carros são concorrentes se as marcas forem diferentes e as categorias forem as mesmas
concorrentes(Modelo1, Modelo2) :-
    carros(_, _, Modelo1, Marca1, Categoria1),
    carros(_, _, Modelo2, Marca2, Categoria2),
    Marca1 \= Marca2,
    Categoria1 = Categoria2.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% concorrentes(Modelo1, Modelo2)
% concorrentes("Mitsubishi Dignity", Modelo2)
% concorrentes("Mitsubishi Dignity", "Cadillac DTS") Renault Primaquatre
% concorrentes("Cadillac DTS", "BYD M6")

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 2 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Carros de luxo se são de determinada marca ou categorias
carro_de_luxo(Modelo) :-
    carros(_, _, Modelo, Marca, Categoria),
    (sub_atom(Marca, _, _, _, "Rolls-Royce");
    sub_atom(Categoria, _, _, _, "Sport");
    Categoria = "Convertible";
    Categoria = "Limousine").

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% carro_de_luxo(Modelo)
% carro_de_luxo("BYD M6")
% carro_de_luxo("Cadillac DTS")

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 3 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encontrar carros que iniciem com uma letra Letra
encontrar_carros_com_letra(Letra, Lista) :-
    findall((Modelo, Marca), (carros(_, _, Modelo, Marca, _), sub_atom(Modelo, 0, 1, _, Letra)), Lista).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% encontrar_carros_com_letra(Letra, Lista)
% encontrar_carros_com_letra("X", Lista)
% encontrar_carros_com_letra("X", [("Xiali N7","FAW Group"), ("Xiali N5","FAW Group")])
% encontrar_carros_com_letra("Z", [("Xiali N7","FAW Group"), ("Xiali N5","FAW Group")])

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 4 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encontrar carros que pertencem a uma determinada Marca
encontrar_carros_de_marca(Marca, Lista) :-
    findall((Modelo, Marca), (carros(_, _, Modelo, Marca, _), sub_atom(Marca, _, _, _, Marca)), Lista).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% encontrar_carros_de_marca(Marca, Lista)
% encontrar_carros_de_marca("ZiL", Lista)
% encontrar_carros_de_marca("ZiL", [("ZIL-118","ZiL"), ("ZIL-4102","ZiL"), ("ZIL-4102","ZiL")])
% encontrar_carros_de_marca("Fiat", [("ZIL-118","ZiL"), ("ZIL-4102","ZiL"), ("ZIL-4102","ZiL")])

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 5 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Encontrar quantos carros por marca
carros_por_marca(Marca):-
aggregate_all(count, carros(_, _, _, Marca, _), Quantidade),
write('Total de carros: '), write(Quantidade), nl.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% carros_por_marca(Marca)
% carros_por_marca("Fiat")
% carros_por_marca("ZiL")

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 6 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Regra para encontrar o modelo mais antigo de uma marca
modelo_mais_antigo(Marca) :-
% Ano Inicio > 1800 garante ano inicio válido AAAA
    findall(AnoInicio-ModeloCompleto, (carros(AnoInicio, _, ModeloCompleto, Marca, _), AnoInicio > 1800), Lista),

    % Ordenar a lista com base no ano de início (do mais antigo para o mais novo)
    sort(Lista, [AnoInicioMaisAntigo-ModeloMaisAntigo|_]),

    % Determinar o ano atual (2025 no exemplo)
    AnoAtual is 2025,

    % Calcular a idade do modelo mais antigo
    Idade is AnoAtual - AnoInicioMaisAntigo,

    % Exibir o modelo e a idade
    write('Modelo: '), write(ModeloMaisAntigo), nl,
    write('Marca: '), write(Marca), nl,
    write('Ano Inicio Fabricação: '), write(AnoInicioMaisAntigo), nl,
    write('Idade do Modelo: '), write(Idade), write(' anos'), nl.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% modelo_mais_antigo(Marca)
% modelo_mais_antigo("Fiat")
% modelo_mais_antigo("Volkswagen")

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 7 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Pega todos os modelos que não pagam mais IPVA no Brasil por marca
modelo_livre_de_ipva_por_marca(Marca, Lista) :-
    AnoAtual is 2025,
% Considera que isenção de IPVA após 15 anos completos de fabricação (maioria dos estados)
    AnoLimite is AnoAtual - 15,
   
    % Coleta todos os modelos que atendem à condição
    findall((Modelo, Marca, AnoFim),
            (carros(_, AnoFim, Modelo, Marca, _), AnoFim <AnoLimite),
            Lista).

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% modelo_livre_de_ipva_por_marca(Marca, Lista)
% modelo_livre_de_ipva_por_marca("Fiat", Lista)
% modelo_livre_de_ipva_por_marca("ZiL", [("ZIL-118","ZiL",1970), ("ZIL-4102","ZiL",1987), ("ZIL-4102","ZiL",1987)])
% modelo_livre_de_ipva_por_marca("Trabant", [("RGW-Auto","Trabant",1972), ("RGW-Auto","Trabant",1972), ("RGW-Auto","Trabant",1972)])

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%% Regra 8 %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
% Informa se uma marca possui ou não pelo menos um carro de luxo. Corte limita a busca a uma aparição true
possui_carros_de_luxo(Marca) :-
    carros(_, _, _, Marca, Categoria),
    (sub_atom(Marca, _, _, _, "Rolls-Royce");
    sub_atom(Categoria, _, _, _, "Sport");
    Categoria = "Convertible";
    Categoria = "Limousine"),
    !.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%% EXEMPLOS DE CONSULTAS %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

% possui_carros_de_luxo(Marca)
% possui_carros_de_luxo("Trabant")
% possui_carros_de_luxo("SEAT")
