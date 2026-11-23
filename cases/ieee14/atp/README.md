# Casos ATP do IEEE 14 (sem IBR)

Decks ATP trifásicos (abc) do caso `cases/ieee14`, com as mesmas máquinas 1d1q, reguladores de tensão
(Static1stOrder) e reguladores de velocidade (Droop1stOrder) de `rms.jl` e `dynamic_phasor.jl`.

| Arquivo | Evento |
|---|---|
| `ieee14_1d1q_gov_avr_trip_ug2.atp` | trip da UG2 em t = 1 s |
| `ieee14_1d1q_gov_avr_curto_linha_b14_13.atp` | curto trifásico na barra 14 em t = 1 s, eliminado em 1,2 s com a abertura da LT13-14 |

Os decks da versão com IBR estão em `cases/ieee14_ibr/atp`. Todos são gerados por `make_atp.py`
(Python 3 + numpy), que resolve o fluxo de potência, calcula a inicialização e escreve os quatro arquivos:

    python cases/ieee14/atp/make_atp.py .

## Como rodar

1. Abra o ATP Launcher (`C:\ATP\tools\ATPLnch.exe`), selecione o `.atp` e use **Run ATP**,
   ou rode `C:\ATP\tools\runATP.exe arquivo.atp`.
2. O ATP gera o `.lis` (listagem e erros) e o `.pl4` (resultados). Abra o `.pl4` no PlotXY.

Passo de 50 µs e horizonte de 10 s, com saída a cada 2 passos (100 µs).

## Base e unidades

O deck usa a base do caso: 100 MVA, 1 Ω = 1 pu de impedância e 1 V = 1 pu de tensão de pico fase-terra
(Clarke invariante em amplitude). Com XOPT = COPT = 60, as reatâncias entram em Ω a 60 Hz e as
susceptâncias em µS, então os dados em pu entram sem conversão. As tensões e correntes do `.pl4` já estão
em pu de pico. A potência trifásica calculada pelo próprio ATP sai multiplicada por 1,5.

## Modelagem

- **Linhas:** RL série com B/2 em cada extremidade.
- **Transformadores:** π do tap fora do nominal só com indutâncias (a do lado "para" é negativa). Com R = 0,
  esse π é exato no tempo para um transformador ideal com reatância de dispersão.
- **Cargas:** impedância constante, R em paralelo com L, a partir de P e Q na tensão do fluxo de potência.
- **Máquinas (1d1q, X'd = X'q, Ra = 0):** equivalente de Norton da tensão atrás da reatância transitória,
  uma fonte de corrente λE/L' em paralelo com L' para a terra, ligada à barra por uma chave (usada no trip e
  para medir a corrente). O rotor, a equação de oscilação (forma com conjugado, Tm = Pm/ω), o AVR e o
  regulador de velocidade estão em MODELS com as equações do PowerSystemTransient, integradas por Euler
  explícito. A fonte é a soma de uma fonte tipo 14 com a injeção de regime, para o ATP partir do fluxo de
  potência, e de uma fonte tipo 60 vinda do MODELS com o desvio em relação a ela.
- **Curto:** chave para a terra com R = 1/99999 pu, como em `rms.jl`. As chaves abrem no instante
  programado (Ie grande), sem esperar o zero de corrente, como nos simuladores do repositório.

## Variáveis gravadas (RECORD do MODELS, em pu do sistema)

Para cada máquina `xx` (01, 02, 03, 06, 08): `Wxx` velocidade, `DLxx` δ (rad), `PExx` conjugado elétrico,
`PMxx` potência mecânica, `EFxx` Efd, `VTxx` tensão terminal, `EDxx`/`EQxx` e'd/e'q, `IDxx`/`IQxx` id/iq.
Tensões das barras: fase a de todas as barras e as três fases das barras 2 e 14. Correntes das chaves dos
geradores e da LT13-14.

## Conferências feitas

- O estado permanente do deck (solução fasorial dos cartões, fase a) reproduz o fluxo de potência com erro
  menor que 1e-7 pu.
- Uma emulação do deck em Python (rede trapezoidal com os mesmos cartões e as equações do MODELS) reproduz
  o fasor dinâmico do PowerSystemTransient com diferenças da ordem de 1e-5 pu na velocidade.

O deck ainda não foi rodado no ATP. Se o ATP acusar erro de sintaxe, o `.lis` mostra a linha.

## Limitação

Como as máquinas e os controles estão em MODELS, com as mesmas equações dos simuladores do repositório, a
comparação com o ATP valida a rede, a integração e a interface máquina-rede, e não o modelo da máquina em
si. Para comparar também com o modelo nativo do ATP, seria preciso usar a máquina tipo 59 (SM59) no
ATPDraw, com X''≈X' e T'' pequenos para aproximar o 1d1q.
