# Casos ATP do IEEE 14 com IBR

Decks ATP trifásicos (abc) do caso `cases/ieee14_ibr`, com a IBR2 no lugar da UG2 e as demais máquinas 1d1q
com AVR e regulador de velocidade.

| Arquivo | Evento |
|---|---|
| `ieee14_ibr_1d1q_gov_avr_trip_ibr2.atp` | trip da IBR2 em t = 1 s |
| `ieee14_ibr_1d1q_gov_avr_curto_linha_b14_13.atp` | curto trifásico na barra 14 em t = 1 s, eliminado em 1,2 s com a abertura da LT13-14 |

A base, as unidades, a modelagem da rede e das máquinas, a forma de rodar e as conferências são as de
`cases/ieee14/atp/README.md`. Os quatro decks são gerados por `cases/ieee14/atp/make_atp.py`.

## IBR

Fonte de corrente (Ip_ef − jIq)·e^(jθ) em MODELS, com os controles do PowerSystemTransient (REPC/REEC/REGC
simplificados, prioridade de Q, ganho de baixa tensão, rampa de Ip, congelamento dos integradores) e a
frequência da estimação por derivada filtrada do ângulo da barra 2 (Tf = 0,05 s, Tw = 0,1 s). θ é o ângulo da
tensão da barra 2, obtido instantaneamente pela transformada de Clarke, como no PowerSystemTransient (sem PLL).
A fonte é a soma de uma fonte tipo 14 (injeção de regime) com uma tipo 60 (desvio vindo do MODELS), ligada
à barra 2 por 1e-6 Ω. No trip, o MODELS zera a corrente total.

Variáveis gravadas da IBR: `IBP` (Pmed), `IBQ` (Qmed), `IBIP` (Ip), `IBIQ` (Iq), `IBVT` (Vt), `IBWF`
(frequência estimada), `IBPR` (Pref), `IBQR` (Qref), em pu do sistema. As das máquinas seguem
`cases/ieee14/atp/README.md`.
