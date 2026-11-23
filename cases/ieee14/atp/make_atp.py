"""Builds the ATP decks of the IEEE 14 case of PowerSystemExperiments, with and without the IBR.

Run from any folder with Python 3 and numpy:
    python make_atp.py <root of PowerSystemExperiments.jl>
It writes cases/ieee14/atp/*.atp and cases/ieee14_ibr/atp/*.atp.

The decks are three-phase (abc) and use the base of the cases, so 1 ohm = 1 pu of impedance and 1 V = 1 pu of
peak phase-to-ground voltage (amplitude invariant Clarke). With XOPT = COPT = 60 the reactances go in ohms at 60 Hz
and the susceptances in micromhos, so the pu data enter the deck as they are.

- Lines: series RL with B/2 at each end. Transformers: pi equivalent of the off-nominal tap with inductances only,
  which is exact in the time domain for an ideal transformer with a leakage reactance (R = 0 in the case).
- Loads: constant impedance, R in parallel with L, from P and Q at the power flow voltage.
- Synchronous machines (1d1q, Xd' = Xq', Ra = 0): Norton equivalent of the voltage behind the transient reactance,
  a current source lambda_E / L' in parallel with L' to the ground. The rotor, the swing equation (torque form,
  Tm = Pm / w), the AVR (Static1stOrder) and the governor (Droop1stOrder) are written in MODELS with the equations of
  PowerSystemTransient. The current source is a type 14 source with the steady state injection, so that ATP starts
  from the power flow, plus a type 60 source from MODELS with the deviation from it.
- IBR: current source (Ip_ef - j Iq) e^(j theta) with the controls of PowerSystemTransient (REPC/REEC/REGC
  simplified), theta the angle of the bus voltage, also split into a type 14 and a type 60 source.
"""

import os
import sys

import numpy as np

FB = 60.0
WB = 2 * np.pi * FB
SB = 100.0
DT = 50e-6
TMAX = 10.0

# ---------------------------------------------------------------------------------------------------------------
# Case data, the same as power_flow.jl and rms.jl
# ---------------------------------------------------------------------------------------------------------------
N_BUS = 14
SHUNT_B = {9: 0.19}
LINES = [  # name, from, to, R, X, B total
    ("LT1-2", 1, 2, 0.0193, 0.0592, 0.0528),
    ("LT1-5", 1, 5, 0.05403, 0.223, 0.0492),
    ("LT2-3", 2, 3, 0.04699, 0.198, 0.0438),
    ("LT2-4", 2, 4, 0.05811, 0.1763, 0.0374),
    ("LT2-5", 2, 5, 0.05695, 0.1739, 0.034),
    ("LT3-4", 3, 4, 0.06701, 0.171, 0.0346),
    ("LT4-5", 4, 5, 0.01335, 0.0421, 0.0128),
    ("LT6-11", 6, 11, 0.09498, 0.1989, 0.0),
    ("LT6-12", 6, 12, 0.12291, 0.2558, 0.0),
    ("LT6-13", 6, 13, 0.06615, 0.1303, 0.0),
    ("LT7-8", 7, 8, 0.0, 0.1761, 0.0),
    ("LT7-9", 7, 9, 0.0, 0.11, 0.0),
    ("LT9-10", 9, 10, 0.03181, 0.0845, 0.0),
    ("LT9-14", 9, 14, 0.12711, 0.2704, 0.0),
    ("LT10-11", 10, 11, 0.08205, 0.1921, 0.0),
    ("LT12-13", 12, 13, 0.22092, 0.1999, 0.0),
    ("LT13-14", 13, 14, 0.17093, 0.348, 0.0),
]
TRAFOS = [  # name, from, to, X, tap on the from side (V_from / a)
    ("TR4-7", 4, 7, 0.2091, 0.978),
    ("TR4-9", 4, 9, 0.5562, 0.969),
    ("TR5-6", 5, 6, 0.252, 0.932),
]
LOADS = {2: (0.217, 0.127), 3: (0.942, 0.19), 4: (0.478, 0.039), 5: (0.076, 0.016), 6: (0.30, 0.30),
         9: (0.295, 0.166), 10: (0.09, 0.058), 11: (0.035, 0.018), 12: (0.061, 0.016), 13: (0.135, 0.058),
         14: (0.149, 0.05)}
PV_P = {2: 0.40, 3: 0.0, 6: 0.0, 8: 0.0}  # generation of the PV buses
V_SET = 1.0

MACHINE = dict(Xd=1.8, Xdp=0.4, Xq=1.7, Xqp=0.4, Ra=0.0, Td0p=8.0, Tq0p=0.4, H=5.0, D=2.0)
GENERATORS = [  # name, bus, Sn, governor
    ("UG1", 1, 286.1881227, True),
    ("UG2", 2, 88.09334324, True),
    ("UG3", 3, 75.889, False),
    ("UG6", 6, 40.722, False),
    ("UG8", 8, 7.1863, False),
]
GOV = dict(R=0.05, Tc=0.01, Tr=2.0)
AVR = dict(K=50.0, T=0.05, Lmn=-5.0, Lmx=5.0)
IBR = dict(name="IBR2", bus=2, Sn=88.09334324, D=20.0, Kpg=0.5, Kig=2.0, Pmax=1.0, Pmin=0.0, Tp=0.1, Kc=0.02,
           Kp=2.0, Ki=10.0, Qmax=1.0, Qmin=-1.0, Tq=0.05, Vfrz=0.7, Vdip=0.9, Kqv=2.0, Iqh1=1.0, Iql1=-1.0,
           Imax=1.1, Tg=0.02, Rrpwr=2.0, lv0=0.4, lv1=0.8, Tf=0.05, Tw=0.1)
FAULT_G = 99999.0


# ---------------------------------------------------------------------------------------------------------------
# Power flow
# ---------------------------------------------------------------------------------------------------------------
def admittance_matrix():
    Y = np.zeros((N_BUS, N_BUS), dtype=complex)
    for _, f, t, r, x, b in LINES:
        y = 1 / complex(r, x)
        f, t = f - 1, t - 1
        Y[f, f] += y + 1j * b / 2
        Y[t, t] += y + 1j * b / 2
        Y[f, t] -= y
        Y[t, f] -= y
    for _, f, t, x, a in TRAFOS:
        y = 1 / complex(0, x)
        f, t = f - 1, t - 1
        Y[f, f] += y / a**2
        Y[t, t] += y
        Y[f, t] -= y / a
        Y[t, f] -= y / a
    for bus, b in SHUNT_B.items():
        Y[bus - 1, bus - 1] += 1j * b
    return Y


def power_flow():
    Y = admittance_matrix()
    P = np.zeros(N_BUS)
    Q = np.zeros(N_BUS)
    for bus, (pl, ql) in LOADS.items():
        P[bus - 1] -= pl
        Q[bus - 1] -= ql
    for bus, pg in PV_P.items():
        P[bus - 1] += pg
    pv = [b - 1 for b in PV_P]
    pq = [i for i in range(N_BUS) if i != 0 and i not in pv]
    V = np.ones(N_BUS)
    th = np.zeros(N_BUS)
    for _ in range(50):
        Vc = V * np.exp(1j * th)
        S = Vc * np.conj(Y @ Vc)
        dP = P - S.real
        dQ = Q - S.imag
        mis = np.concatenate([dP[1:], dQ[pq]])
        if np.max(np.abs(mis)) < 1e-13:
            break
        # numerical jacobian of the injections with respect to th[1:] and V[pq]
        x0 = np.concatenate([th[1:], V[pq]])

        def f(x):
            t2 = th.copy()
            v2 = V.copy()
            t2[1:] = x[:N_BUS - 1]
            v2[pq] = x[N_BUS - 1:]
            vc = v2 * np.exp(1j * t2)
            s = vc * np.conj(Y @ vc)
            return np.concatenate([s.real[1:], s.imag[pq]])

        J = np.zeros((len(x0), len(x0)))
        f0 = f(x0)
        for k in range(len(x0)):
            xk = x0.copy()
            xk[k] += 1e-7
            J[:, k] = (f(xk) - f0) / 1e-7
        dx = np.linalg.solve(J, mis)
        th[1:] += dx[:N_BUS - 1]
        V[pq] += dx[N_BUS - 1:]
    Vc = V * np.exp(1j * th)
    S = Vc * np.conj(Y @ Vc)
    return V, th, S


# ---------------------------------------------------------------------------------------------------------------
# ATP card helpers
# ---------------------------------------------------------------------------------------------------------------
def e16(x):
    s = f"{x:16.9E}"
    assert len(s) == 16, s
    return s


def f10(x):
    for digits in range(9, 0, -1):
        s = f"{x:.{digits}g}".replace("e", "E")
        if "." not in s:
            s = s.replace("E", ".E") if "E" in s else s + "."
        if len(s) <= 10:
            return s.rjust(10)
    raise ValueError(x)


def node(name):
    assert len(name) <= 6, name
    return name.ljust(6)


def rlc(n1, n2, r=0.0, x=0.0, c=0.0, out=0):
    """RLC branch in the $VINTAGE, 1 format: R 27-42, L (X in ohms) 43-58, C (B in umho) 59-74, output col 80."""
    line = "  " + node(n1) + node(n2) + " " * 12
    line += (e16(r) if r != 0 else " " * 16) + (e16(x) if x != 0 else " " * 16)
    line += (e16(c) if c != 0 else " " * 16)
    line = line.ljust(79) + (str(out) if out else " ")
    assert len(line) == 80
    return line.rstrip()


def switch(n1, n2, tclose, topen, ie=0.0, out=0):
    line = "  " + node(n1) + node(n2) + f10(tclose) + f10(topen) + f10(ie)
    line = line.ljust(79) + (str(out) if out else " ")
    return line.rstrip()


def source14_current(n, amp, phase_deg):
    line = "14" + node(n) + "-1" + f10(amp) + f10(FB) + f10(phase_deg) + " " * 20 + f10(-1.0) + f10(1000.0)
    assert len(line) == 80
    return line


def source60_current(n):
    line = "60" + node(n) + "-1" + " " * 50 + f10(0.0) + f10(1000.0)
    assert len(line) == 80
    return line


PH = "ABC"
SHIFT = [0.0, -120.0, 120.0]


def bus_node(bus, p):
    return f"B{bus:02d}{PH[p]}"


# ---------------------------------------------------------------------------------------------------------------
# Initial states, the same as PowerSystemTransient
# ---------------------------------------------------------------------------------------------------------------
def machine_init(gen, V, th, S):
    name, bus, Sn, gov = gen
    k = SB / Sn
    xd, xdp, xq, xqp = MACHINE["Xd"] * k, MACHINE["Xdp"] * k, MACHINE["Xq"] * k, MACHINE["Xqp"] * k
    pl, ql = LOADS.get(bus, (0.0, 0.0))
    S0 = S[bus - 1] + complex(pl, ql)
    V0 = V[bus - 1] * np.exp(1j * th[bus - 1])
    I0 = np.conj(S0 / V0)
    E = V0 + 1j * xq * I0
    delta = np.angle(E)
    rot = np.exp(-1j * (delta - np.pi / 2))
    vdq = V0 * rot
    idq = I0 * rot
    vd, vq, i_d, i_q = vdq.real, vdq.imag, idq.real, idq.imag
    edp = vd - xqp * i_q
    eqp = vq + xdp * i_d
    efd = eqp + (xd - xdp) * i_d
    pe = edp * i_d + eqp * i_q
    vt = abs(V0)
    # Norton current of the steady state, in the synchronous frame
    c0 = complex(eqp, -edp) / xdp
    IN0 = c0 * np.exp(1j * (delta - np.pi / 2))
    return dict(name=name, bus=bus, gov=gov, xd=xd, xdp=xdp, xq=xq, tdo=MACHINE["Td0p"], tqo=MACHINE["Tq0p"],
                hh=MACHINE["H"] / k, dd=MACHINE["D"] / k, rgov=GOV["R"] * k, tc=GOV["Tc"], tr=GOV["Tr"],
                kavr=AVR["K"], tavr=AVR["T"], efmin=AVR["Lmn"], efmax=AVR["Lmx"], edp0=edp, eqp0=eqp,
                dlt0=delta, efd0=efd, pm0=pe, vref=vt + efd / AVR["K"], pref=pe, IN0=IN0, P0=S0.real,
                Q0=S0.imag)


def ibr_init(V, th, S):
    bus = IBR["bus"]
    k = IBR["Sn"] / SB
    pl, ql = LOADS.get(bus, (0.0, 0.0))
    S0 = S[bus - 1] + complex(pl, ql)
    vt = V[bus - 1]
    theta = th[bus - 1]
    ip0 = S0.real / vt
    iq0 = S0.imag / vt
    kc = IBR["Kc"] / k
    I0 = complex(ip0, -iq0) * np.exp(1j * theta)
    return dict(bus=bus, d=IBR["D"] * k, kpg=IBR["Kpg"], kig=IBR["Kig"], pmax=IBR["Pmax"] * k,
                pmin=IBR["Pmin"] * k, tp=IBR["Tp"], kc=kc, kp=IBR["Kp"] * k, ki=IBR["Ki"] * k,
                qmax=IBR["Qmax"] * k, qmin=IBR["Qmin"] * k, tq=IBR["Tq"], vfrz=IBR["Vfrz"], vdip=IBR["Vdip"],
                kqv=IBR["Kqv"] * k, iqh1=IBR["Iqh1"] * k, iql1=IBR["Iql1"] * k, imax=IBR["Imax"] * k,
                tg=IBR["Tg"], rrpwr=IBR["Rrpwr"] * k, lv0=IBR["lv0"], lv1=IBR["lv1"], tf=IBR["Tf"],
                tw=IBR["Tw"], v0=vt, th0=theta, ip0=ip0, iq0=iq0, pset=S0.real, vref=vt + kc * S0.imag,
                q0=S0.imag, I0=I0, P0=S0.real, Q0=S0.imag)


# ---------------------------------------------------------------------------------------------------------------
# MODELS
# ---------------------------------------------------------------------------------------------------------------
MODEL_SM = """\
MODEL sm1d1q
-- One d one q machine of PowerSystemTransient (Xd' = Xq', Ra = 0) with the
-- Static1stOrder AVR and the Droop1stOrder governor, all in the system base.
-- The output is the deviation of the Norton current lambda_E / L' from the
-- steady state current of the type 14 source, per phase.
DATA xd, xq, xdp, tdo, tqo, hh, dd, gov, rgov, tc, tr
DATA kavr, tavr, efmin, efmax
DATA edp0, eqp0, dlt0, efd0, pm0, vref, pref
CONST wb {val: 376.99111843077517}
INPUT va, vb, vc, ia, ib, ic
OUTPUT ina, inb, inc
VAR ina, inb, inc, edp, eqp, dlt, w, efdu, efd, pm1, pm, pe, vt
VAR valf, vbet, ialf, ibet, thr, sid, siq, dedp, deqp, dw, ddlt
VAR defdu, dpm1, dpm, cr, ci, cr0, ci0, th1, th0, s3
INIT
  edp := edp0
  eqp := eqp0
  dlt := dlt0
  w := 1
  efdu := efd0
  efd := efd0
  pm1 := pm0
  pm := pm0
  pe := pm0
  vt := 0
  sid := 0
  siq := 0
  s3 := sqrt(3)
  cr0 := eqp0 / xdp
  ci0 := -edp0 / xdp
  ina := 0
  inb := 0
  inc := 0
ENDINIT
EXEC
  -- Clarke of the terminal voltage and of the stator current at t
  valf := (2 * va - vb - vc) / 3
  vbet := (vb - vc) / s3
  ialf := (2 * ia - ib - ic) / 3
  ibet := (ib - ic) / s3
  vt := sqrt(valf * valf + vbet * vbet)
  thr := wb * t + dlt - pi / 2
  sid := ialf * cos(thr) + ibet * sin(thr)
  siq := -ialf * sin(thr) + ibet * cos(thr)
  pe := edp * sid + eqp * siq
  -- derivatives at t
  dedp := (-edp + (xq - xdp) * siq) / tqo
  deqp := (-eqp - (xd - xdp) * sid + efd) / tdo
  dw := (pm / w - pe - dd * (w - 1)) / (2 * hh)
  ddlt := wb * (w - 1)
  defdu := (kavr * (vref - vt) - efdu) / tavr
  IF gov > 0.5 THEN
    dpm1 := (pref + (1 - w) / rgov - pm1) / tc
    dpm := (pm1 - pm) / tr
  ELSE
    dpm1 := 0
    dpm := 0
  ENDIF
  -- explicit Euler from t to t + timestep
  edp := edp + timestep * dedp
  eqp := eqp + timestep * deqp
  w := w + timestep * dw
  dlt := dlt + timestep * ddlt
  efdu := efdu + timestep * defdu
  pm1 := pm1 + timestep * dpm1
  pm := pm + timestep * dpm
  efd := min(max(efdu, efmin), efmax)
  -- Norton current at t + timestep, minus the steady state current
  cr := eqp / xdp
  ci := -edp / xdp
  th1 := wb * (t + timestep) + dlt - pi / 2
  th0 := wb * (t + timestep) + dlt0 - pi / 2
  ina := cr * cos(th1) - ci * sin(th1) - cr0 * cos(th0) + ci0 * sin(th0)
  th1 := th1 - 2 * pi / 3
  th0 := th0 - 2 * pi / 3
  inb := cr * cos(th1) - ci * sin(th1) - cr0 * cos(th0) + ci0 * sin(th0)
  th1 := th1 + 4 * pi / 3
  th0 := th0 + 4 * pi / 3
  inc := cr * cos(th1) - ci * sin(th1) - cr0 * cos(th0) + ci0 * sin(th0)
ENDEXEC
ENDMODEL
"""

MODEL_IBR = """\
MODEL ibrwecc
-- IBR of PowerSystemTransient: REPC/REEC/REGC simplified, Q priority, the
-- frequency from the filtered angle derivative of its bus, all in the system
-- base. The output is the deviation of the current from the steady state
-- current of the type 14 source, per phase. ttrip is the trip time.
DATA d, kpg, kig, pmax, pmin, tp, kc, kp, ki, qmax, qmin, tq
DATA vfrz, vdip, kqv, iqh1, iql1, imax, tg, rrpwr, lv0, lv1, tf, tw
DATA v0, th0, ip0, iq0, pset, vref, q0, ttrip
CONST wb {val: 376.99111843077517}
INPUT va, vb, vc
OUTPUT ina, inb, inc
VAR ina, inb, inc, yp, pref, yq, qref, ip, iq, xth, wf, the, vt
VAR valf, vbet, vr, vi, thr, dif, lv, ipef, pmed, qmed, dom, dwf
VAR ep, xp, pext, dyp, dpref, eqv, xq, qext, dyq, dqref, iqinj
VAR vtf, ipc, iqc, iqcmd, ipmax, ipcmd, dip, diq, s3, ph, lv00
VAR ipef0, frzp, frzq, dipf
INIT
  yp := pset
  pref := pset
  yq := q0
  qref := q0
  ip := ip0
  iq := iq0
  xth := 0
  wf := 1
  the := th0
  vt := v0
  s3 := sqrt(3)
  ipef0 := ip0
  pmed := pset
  qmed := q0
  ina := 0
  inb := 0
  inc := 0
ENDINIT
EXEC
  -- bus voltage in the synchronous frame and its continuous angle at t
  valf := (2 * va - vb - vc) / 3
  vbet := (vb - vc) / s3
  vr := valf * cos(wb * t) + vbet * sin(wb * t)
  vi := vbet * cos(wb * t) - valf * sin(wb * t)
  vt := sqrt(vr * vr + vi * vi)
  thr := atan2(vi, vr)
  dif := thr - the
  IF dif > pi THEN
    dif := dif - 2 * pi
  ELSIF dif < -pi THEN
    dif := dif + 2 * pi
  ENDIF
  the := the + dif
  -- low voltage gain and measured powers
  IF vt <= lv0 THEN
    lv := 0
  ELSIF vt >= lv1 THEN
    lv := 1
  ELSE
    lv := (vt - lv0) / (lv1 - lv0)
  ENDIF
  ipef := lv * ip
  IF t < ttrip THEN
    pmed := vt * ipef
    qmed := vt * iq
  ELSE
    pmed := 0
    qmed := 0
  ENDIF
  -- frequency estimation
  dom := ((the - th0) / wb - xth) / tf
  dwf := (dom + 1 - wf) / tw
  -- active power control
  ep := d * (1 - wf) + pset - pmed
  xp := kpg * ep
  pext := min(max(xp + yp, pmin), pmax)
  frzp := 0
  IF vt < vdip THEN
    frzp := 1
  ENDIF
  IF xp + yp >= pmax AND ep > 0 THEN
    frzp := 1
  ENDIF
  IF xp + yp <= pmin AND ep < 0 THEN
    frzp := 1
  ENDIF
  dyp := kig * ep * (1 - frzp)
  dpref := (pext - pref) / tp
  -- reactive power control
  eqv := vref - vt - kc * qmed
  xq := kp * eqv
  qext := min(max(xq + yq, qmin), qmax)
  frzq := 0
  IF vt < vfrz THEN
    frzq := 1
  ENDIF
  IF xq + yq >= qmax AND eqv > 0 THEN
    frzq := 1
  ENDIF
  IF xq + yq <= qmin AND eqv < 0 THEN
    frzq := 1
  ENDIF
  dyq := ki * eqv * (1 - frzq)
  dqref := (qext - qref) / tq
  -- current logic with Q priority
  IF vt < vdip THEN
    iqinj := min(max(kqv * (v0 - vt), iql1), iqh1)
  ELSE
    iqinj := 0
  ENDIF
  vtf := max(vt, 0.001)
  ipc := pref / vtf
  iqc := iqinj + qref / vtf
  iqcmd := min(max(iqc, -imax), imax)
  ipmax := sqrt(imax * imax - iqcmd * iqcmd)
  ipcmd := min(max(ipc, 0), ipmax)
  -- converter with the ramp limit of Ip
  dipf := (ipcmd - ip) / tg
  IF dipf > rrpwr THEN
    dipf := rrpwr
  ENDIF
  diq := (iqcmd - iq) / tg
  -- explicit Euler from t to t + timestep
  yp := yp + timestep * dyp
  pref := pref + timestep * dpref
  yq := yq + timestep * dyq
  qref := qref + timestep * dqref
  ip := ip + timestep * dipf
  iq := iq + timestep * diq
  xth := xth + timestep * dom
  wf := wf + timestep * dwf
  -- current at t + timestep with the angle at t, minus the steady state
  ipef := lv * ip
  IF t + timestep >= ttrip THEN
    ipef := 0
    iq := 0
  ENDIF
  ph := the + wb * (t + timestep)
  lv00 := th0 + wb * (t + timestep)
  ina := ipef * cos(ph) + iq * sin(ph) - ipef0 * cos(lv00) - iq0 * sin(lv00)
  ph := ph - 2 * pi / 3
  lv00 := lv00 - 2 * pi / 3
  inb := ipef * cos(ph) + iq * sin(ph) - ipef0 * cos(lv00) - iq0 * sin(lv00)
  ph := ph + 4 * pi / 3
  lv00 := lv00 + 4 * pi / 3
  inc := ipef * cos(ph) + iq * sin(ph) - ipef0 * cos(lv00) - iq0 * sin(lv00)
ENDEXEC
ENDMODEL
"""


def data_lines(pairs):
    # one DATA group, an assignment per line, separated by commas
    lines = []
    for k, (key, value) in enumerate(pairs):
        head = "  DATA " if k == 0 else "       "
        tail = "," if k < len(pairs) - 1 else ""
        lines.append(f"{head}{key} := {value:.15g}{tail}")
    return lines


def models_section(machines, ibr):
    lines = ["MODELS", "INPUT"]
    for m in machines:
        b = m["bus"]
        for p in range(3):
            lines.append(f"  V{b:02d}{PH[p]} {{v({bus_node(b, p)})}}")
        for p in range(3):
            lines.append(f"  I{b:02d}{PH[p]} {{i(G{b:02d}{PH[p]})}}")
    if ibr is not None:
        b = ibr["bus"]
        for p in range(3):
            lines.append(f"  W{b:02d}{PH[p]} {{v({bus_node(b, p)})}}")
    lines.append("OUTPUT")
    for m in machines:
        b = m["bus"]
        lines += [f"  G{b:02d}{PH[p]}" for p in range(3)]
    if ibr is not None:
        b = ibr["bus"]
        lines += [f"  R{b:02d}{PH[p]}" for p in range(3)]
    lines += MODEL_SM.rstrip("\n").split("\n")
    if ibr is not None:
        lines += MODEL_IBR.rstrip("\n").split("\n")
    for m in machines:
        b = m["bus"]
        lines.append(f"USE sm1d1q AS {m['name']}")
        keys = ["xd", "xq", "xdp", "tdo", "tqo", "hh", "dd"]
        pairs = [(k, m[k]) for k in keys] + [("gov", 1.0 if m["gov"] else 0.0)]
        pairs += [(k, m[k]) for k in ["rgov", "tc", "tr", "kavr", "tavr", "efmin", "efmax", "edp0", "eqp0",
                                      "dlt0", "efd0", "pm0", "vref", "pref"]]
        lines += data_lines(pairs)
        lines.append(f"  INPUT va := V{b:02d}A, vb := V{b:02d}B, vc := V{b:02d}C,")
        lines.append(f"        ia := I{b:02d}A, ib := I{b:02d}B, ic := I{b:02d}C")
        lines.append(f"  OUTPUT G{b:02d}A := ina, G{b:02d}B := inb, G{b:02d}C := inc")
        lines.append("ENDUSE")
    if ibr is not None:
        b = ibr["bus"]
        lines.append("USE ibrwecc AS IBR2")
        keys = ["d", "kpg", "kig", "pmax", "pmin", "tp", "kc", "kp", "ki", "qmax", "qmin", "tq", "vfrz", "vdip",
                "kqv", "iqh1", "iql1", "imax", "tg", "rrpwr", "lv0", "lv1", "tf", "tw", "v0", "th0", "ip0", "iq0",
                "pset", "vref", "q0", "ttrip"]
        lines += data_lines([(k, ibr[k]) for k in keys])
        lines.append(f"  INPUT va := W{b:02d}A, vb := W{b:02d}B, vc := W{b:02d}C")
        lines.append(f"  OUTPUT R{b:02d}A := ina, R{b:02d}B := inb, R{b:02d}C := inc")
        lines.append("ENDUSE")
    lines.append("RECORD")
    for m in machines:
        b = m["bus"]
        for var, short in [("w", "W"), ("dlt", "DL"), ("pe", "PE"), ("pm", "PM"), ("efd", "EF"), ("vt", "VT"),
                           ("edp", "ED"), ("eqp", "EQ"), ("sid", "ID"), ("siq", "IQ")]:
            lines.append(f"  {m['name']}.{var} AS {short}{b:02d}")
    if ibr is not None:
        for var, short in [("pmed", "IBP"), ("qmed", "IBQ"), ("ip", "IBIP"), ("iq", "IBIQ"), ("vt", "IBVT"),
                           ("wf", "IBWF"), ("pref", "IBPR"), ("qref", "IBQR")]:
            lines.append(f"  IBR2.{var} AS {short}")
    lines.append("ENDMODELS")
    for line in lines:
        assert len(line) <= 80, line
    return lines


# ---------------------------------------------------------------------------------------------------------------
# Deck
# ---------------------------------------------------------------------------------------------------------------
def deck(title, V, th, S, with_ibr, event):
    gens = [g for g in GENERATORS if not (with_ibr and g[0] == "UG2")]
    machines = [machine_init(g, V, th, S) for g in gens]
    ibr = None
    if with_ibr:
        ibr = ibr_init(V, th, S)
        ibr["ttrip"] = 1.0 if event == "trip" else 1.0e3

    out = ["BEGIN NEW DATA CASE", "C " + title]
    out += ["C Generated by make_atp.py from the data of power_flow.jl and rms.jl.",
            "C Base: 100 MVA, 1 ohm = 1 pu, 1 V = 1 pu peak phase-to-ground.",
            "C XOPT = COPT = 60: L field = X in ohm at 60 Hz, C field = B in umho.",
            "C  dT  >< Tmax >< Xopt >< Copt >",
            "   5.E-5     10.     60.     60.",
            "   10000       2       0       0       1       0       0       1       0"]
    out += models_section(machines, ibr)

    br = ["C Branches", "$VINTAGE, 1"]
    br.append("C < n1 >< n2 ><ref1><ref2><       R      ><  X (ohm @60Hz)><    B (umho)    >")
    for name, f, t, r, x, b in LINES:
        br.append(f"C {name}")
        for p in range(3):
            n_from = bus_node(f, p)
            if name == "LT13-14":
                n_from = f"M13{PH[p]}"  # behind the switch that opens the line at bus 13
            br.append(rlc(n_from, bus_node(t, p), r=r, x=x))
            if b > 0:
                br.append(rlc(bus_node(f, p), "", c=b / 2 * 1e6))
                br.append(rlc(bus_node(t, p), "", c=b / 2 * 1e6))
    for name, f, t, x, a in TRAFOS:
        br.append(f"C {name}: pi of the tap {a}, inductances only")
        for p in range(3):
            br.append(rlc(bus_node(f, p), bus_node(t, p), x=a * x))
            br.append(rlc(bus_node(f, p), "", x=a * a * x / (1 - a)))
            br.append(rlc(bus_node(t, p), "", x=a * x / (a - 1)))
    for bus, bsh in SHUNT_B.items():
        br.append(f"C capacitor bank of bus {bus}")
        for p in range(3):
            br.append(rlc(bus_node(bus, p), "", c=bsh * 1e6))
    br.append("C Loads: constant impedance, R // L at the power flow voltage")
    for bus, (pl, ql) in LOADS.items():
        v2 = V[bus - 1] ** 2
        for p in range(3):
            br.append(rlc(bus_node(bus, p), "", r=v2 / pl))
            br.append(rlc(bus_node(bus, p), "", x=v2 / ql))
    br.append("C Machines: L' of the Norton equivalent, from the internal node to the ground")
    for m in machines:
        for p in range(3):
            br.append(rlc(f"G{m['bus']:02d}{PH[p]}", "", x=m["xdp"]))
    if event == "short":
        br.append(f"C Fault resistance of bus 14, 1 / {FAULT_G:g} pu")
        for p in range(3):
            br.append(rlc(f"F14{PH[p]}", "", r=1 / FAULT_G))
    br += ["$VINTAGE, 0", "BLANK BRANCH"]
    out += br

    sw = ["C Switches", "C < n1 >< n2 >< Tclose >< Top    ><  Ie    >"]
    for m in machines:
        topen = 1.0 if (event == "trip" and m["name"] == "UG2") else 1000.0
        for p in range(3):
            sw.append(switch(f"G{m['bus']:02d}{PH[p]}", bus_node(m["bus"], p), -1.0, topen, 1.0e9, out=1))
    for p in range(3):
        topen = 1.2 if event == "short" else 1000.0
        sw.append(switch(bus_node(13, p), f"M13{PH[p]}", -1.0, topen, 1.0e9, out=1))
    if event == "short":
        for p in range(3):
            sw.append(switch(bus_node(14, p), f"F14{PH[p]}", 1.0, 1.2, 1.0e9, out=1))
    sw.append("BLANK SWITCH")
    out += sw

    src = ["C Sources: steady state current (type 14) plus deviation from MODELS (type 60)"]
    for m in machines:
        amp = abs(m["IN0"])
        ang = np.degrees(np.angle(m["IN0"]))
        for p in range(3):
            n = f"G{m['bus']:02d}{PH[p]}"
            src.append(source14_current(n, amp, ang + SHIFT[p]))
            src.append(source60_current(n))
    if ibr is not None:
        amp = abs(ibr["I0"])
        ang = np.degrees(np.angle(ibr["I0"]))
        for p in range(3):
            n = f"R{ibr['bus']:02d}{PH[p]}"
            src.append(source14_current(n, amp, ang + SHIFT[p]))
            src.append(source60_current(n))
    src.append("BLANK SOURCE")
    out += src
    if ibr is not None:
        # the IBR sources sit on their own node, joined to the bus by a resistance of 1e-6 ohm
        idx = out.index("$VINTAGE, 0")
        extra = ["C IBR node, joined to bus 2 by 1e-6 ohm"]
        for p in range(3):
            extra.append(rlc(f"R02{PH[p]}", bus_node(2, p), r=1e-6))
        out[idx:idx] = extra

    nodes = [bus_node(b, 0) for b in range(1, N_BUS + 1)] + [bus_node(14, 1), bus_node(14, 2), bus_node(2, 1),
                                                           bus_node(2, 2)]
    for k in range(0, len(nodes), 13):
        out.append("  " + "".join(node(n) for n in nodes[k:k + 13]))
    out += ["BLANK OUTPUT", "BLANK PLOT", "BEGIN NEW DATA CASE", "BLANK", ""]
    for line in out:
        assert len(line) <= 80, line
    return "\n".join(out), machines, ibr


def summary(V, th, S, machines, ibr):
    lines = ["Power flow", "bus  V (pu)     theta (deg)"]
    for i in range(N_BUS):
        lines.append(f"{i + 1:3d}  {V[i]:.10f}  {np.degrees(th[i]):.8f}")
    lines.append("")
    lines.append("machine  P0 (pu)      Q0 (pu)      delta (rad)   efd (pu)     e'd          e'q")
    for m in machines:
        lines.append(f"{m['name']:7s}  {m['P0']:+.8f}  {m['Q0']:+.8f}  {m['dlt0']:+.8f}  {m['efd0']:+.8f}  "
                     f"{m['edp0']:+.8f}  {m['eqp0']:+.8f}")
    if ibr is not None:
        lines.append(f"IBR2     P0 = {ibr['P0']:+.8f}  Q0 = {ibr['Q0']:+.8f}  Vref = {ibr['vref']:.8f}")
    return "\n".join(lines) + "\n"


def main(root):
    V, th, S = power_flow()
    cases = [
        ("ieee14", False, "trip", "ieee14_1d1q_gov_avr_trip_ug2.atp",
         "IEEE 14, 1d1q + AVR + governor, trip of UG2 at 1 s"),
        ("ieee14", False, "short", "ieee14_1d1q_gov_avr_curto_linha_b14_13.atp",
         "IEEE 14, 1d1q + AVR + governor, fault at bus 14 at 1 s, LT13-14 open at 1.2 s"),
        ("ieee14_ibr", True, "trip", "ieee14_ibr_1d1q_gov_avr_trip_ibr2.atp",
         "IEEE 14 with IBR2 in place of UG2, trip of IBR2 at 1 s"),
        ("ieee14_ibr", True, "short", "ieee14_ibr_1d1q_gov_avr_curto_linha_b14_13.atp",
         "IEEE 14 with IBR2, fault at bus 14 at 1 s, LT13-14 open at 1.2 s"),
    ]
    for case, with_ibr, event, fname, title in cases:
        folder = os.path.join(root, "cases", case, "atp")
        os.makedirs(folder, exist_ok=True)
        text, machines, ibr = deck(title, V, th, S, with_ibr, event)
        with open(os.path.join(folder, fname), "w", newline="\r\n") as fh:
            fh.write(text)
        with open(os.path.join(folder, "initial_conditions.txt"), "w", newline="\r\n") as fh:
            fh.write(summary(V, th, S, machines, ibr))
        print("written", os.path.join(folder, fname))


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else ".")
