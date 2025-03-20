(ns invest_simulator.core)

(defn calcular-valor-investido [aporte-inicial aporte-mensal anos]
  (let [meses (* anos 12)]  
    (+ aporte-inicial (* aporte-mensal meses))))  

(defn calcular-montante [aporte-inicial aporte-mensal taxa-anual tempo-anos]
  (let [taxa-mensal (- (Math/pow (+ 1 (/ taxa-anual 100)) (/ 1 12)) 1)  
        tempo-meses (* tempo-anos 12)  
        montante-inicial (* aporte-inicial (Math/pow (+ 1 taxa-mensal) tempo-meses))
        montante-mensal (* aporte-mensal (/ (- (Math/pow (+ 1 taxa-mensal) tempo-meses) 1) taxa-mensal))]
    (+ montante-inicial montante-mensal)))
