(ns invest_simulator.view
  (:require [hiccup.page :as page]))

(def investimentos
  [{:nome "Vale" :rendimento 12.5}
   {:nome "Poupança" :rendimento 5.0}
   {:nome "S&P 500" :rendimento 7.2}
   {:nome "Petrobras" :rendimento 9.3}
   {:nome "Banco do Brasil" :rendimento 6.8}])

(defn script-js []
  (page/html5
   [:script
    "function atualizarRendimento(select) {
       var rendimento = select.options[select.selectedIndex].getAttribute('data-rendimento');
       document.getElementById('rendimento').value = rendimento;  // Atualiza o campo oculto
       document.getElementById('rendimento-exibicao').value = rendimento + '% ao ano';  // Atualiza o campo de exibição
    }"]))

(defn inicio []
  (page/html5
   [:head 
    [:title "Simulador de Investimentos"]
    (page/include-css "/css/style.css") 
    (script-js)]  
   [:body
    [:h1 "Simulador de Investimentos"]
    [:form {:action "/simular" :method "post"}

     [:label "Escolha o tipo de investimento:"]
     [:select {:name "investimento" :onchange "atualizarRendimento(this)"}
      [:option {:value "" :selected true :disabled true} "Nenhum investimento selecionado"] ;; Opção default
      (for [inv investimentos]
        [:option {:value (:nome inv) :data-rendimento (:rendimento inv)} 
         (str (:nome inv))])]   ;; Lista suspensa com dados de rendimento como atributo "data-rendimento"
     
     [:input {:type "hidden" :name "rendimento" :id "rendimento"}]  ;; Campo oculto para o valor do rendimento

     [:label "Rendimento selecionado:"]
     [:input {:type "text" :name "rendimento-exibicao" :id "rendimento-exibicao" :readonly true}]  ;; Exibição do rendimento (campo de texto)

     [:label "Aporte Inicial:"]
     [:input {:type "number" :name "aporte-inicial" :placeholder "Digite o aporte inicial"}]

     [:label "Aporte Mensal:"]
     [:input {:type "number" :name "aporte-mensal" :placeholder "Digite o aporte mensal"}]
     
     [:button "Simular"]]]))

(defn render-simulacao 
  [
    rendimento-1-ano rendimento-5-anos rendimento-10-anos
    investido-1-ano investido-5-anos investido-10-anos
  ]
  (page/html5
   [:head [:title "Resultados da Simulação"]
   (page/include-css "/css/style.css")]
   [:body
    [:h1 "Resultados"]
    [:div {:class "result"}
      [:div {:class "ano1"}
        [:h3 "Resultados após 1 ano"]
        [:p (str "Investido: R$" (format "%.2f" investido-1-ano))]
        [:p (str "Valor total: R$" (format "%.2f" rendimento-1-ano))]
      ]
      [:div {:class "ano1"}
        [:h3 "Resultados após 5 anos"]
        [:p (str "Investido: R$" (format "%.2f" investido-5-anos))]
        [:p (str "Valor total: R$" (format "%.2f" rendimento-5-anos))]
      ]
      [:div {:class "ano1"}
        [:h3 "Resultados após 10 anos"]
        [:p (str "Investido: R$" (format "%.2f" investido-10-anos))]
        [:p (str "Valor total: R$" (format "%.2f" rendimento-10-anos))]
      ]
      [:button {:onclick "window.location.href='/inicio'"} "Voltar"]
    ]]))
