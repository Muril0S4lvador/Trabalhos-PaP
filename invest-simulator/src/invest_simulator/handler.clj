(ns invest_simulator.handler
  (:require [compojure.core :refer :all]
            [compojure.route :as route]
            [ring.middleware.defaults :refer [wrap-defaults api-defaults]]
            [ring.middleware.resource :refer [wrap-resource]]
            [invest_simulator.core :as core]
            [invest_simulator.view :as view]))

(defroutes app-routes
  (GET "/" [] "Programa Rodando!")
  (GET "/inicio" [] (view/inicio))
  (POST "/simular" [aporte-inicial aporte-mensal rendimento :as request]
    (let [aporte-inicial (if (empty? aporte-inicial) 0.0 (Double/parseDouble aporte-inicial))  
        aporte-mensal (if (empty? aporte-mensal) 0.0 (Double/parseDouble aporte-mensal))    
        rendimento (if (empty? rendimento) 0.0 (Double/parseDouble rendimento))]
      (let [resultado-1-ano (core/calcular-montante aporte-inicial aporte-mensal rendimento 1)
            resultado-5-anos (core/calcular-montante aporte-inicial aporte-mensal rendimento 5)
            resultado-10-anos (core/calcular-montante aporte-inicial aporte-mensal rendimento 10)
            investido-1-ano (core/calcular-valor-investido aporte-inicial aporte-mensal 1)
            investido-5-anos (core/calcular-valor-investido aporte-inicial aporte-mensal 5)
            investido-10-anos (core/calcular-valor-investido aporte-inicial aporte-mensal 10)]
        (view/render-simulacao resultado-1-ano resultado-5-anos resultado-10-anos investido-1-ano investido-5-anos investido-10-anos)
        )))
  (route/not-found "Not Found"))

(def app
  (-> app-routes
      (wrap-defaults api-defaults)
      (wrap-resource "public")))
