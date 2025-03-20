(ns invest-simulator.handler-test
  (:require [clojure.test :refer :all]
            [ring.mock.request :as mock]
            [invest_simulator.handler :refer :all]))

(deftest test-app
  (testing "main route"
    (let [response (app (mock/request :get "/"))]
      (is (= (:status response) 200))
      (is (= (:body response) "Programa Rodando!"))))

  (testing "main route 2"
    (let [response (app (mock/request :get "/"))]
      (is (= (:status response) 200))
      (is (= (:body response) "Retorna Erro"))))

  (testing "not-found route"
    (let [response (app (mock/request :get "/invalid"))]
      (is (= (:status response) 404)))))
