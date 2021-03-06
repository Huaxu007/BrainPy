# -*- coding: utf-8 -*-

"""
Test the network scaling ability.
"""


import time
import brainpy as bp
import numpy as np


def define_hh(E_Na=50., g_Na=120., E_K=-77., g_K=36., E_Leak=-54.387,
              g_Leak=0.03, C=1.0, Vth=20., Iext=10.):
    ST = bp.types.NeuState(
        {'V': -65., 'm': 0., 'h': 0., 'n': 0., 'sp': 0., 'inp': 0.},
        help='Hodgkin–Huxley neuron state.\n'
             '"V" denotes membrane potential.\n'
             '"n" denotes potassium channel activation probability.\n'
             '"m" denotes sodium channel activation probability.\n'
             '"h" denotes sodium channel inactivation probability.\n'
             '"sp" denotes spiking state.\n'
             '"inp" denotes synaptic input.\n'
    )

    @bp.integrate
    def int_m(m, t, V):
        alpha = 0.1 * (V + 40) / (1 - np.exp(-(V + 40) / 10))
        beta = 4.0 * np.exp(-(V + 65) / 18)
        return alpha * (1 - m) - beta * m

    @bp.integrate
    def int_h(h, t, V):
        alpha = 0.07 * np.exp(-(V + 65) / 20.)
        beta = 1 / (1 + np.exp(-(V + 35) / 10))
        return alpha * (1 - h) - beta * h

    @bp.integrate
    def int_n(n, t, V):
        alpha = 0.01 * (V + 55) / (1 - np.exp(-(V + 55) / 10))
        beta = 0.125 * np.exp(-(V + 65) / 80)
        return alpha * (1 - n) - beta * n

    @bp.integrate
    def int_V(V, t, m, h, n, Isyn):
        INa = g_Na * m ** 3 * h * (V - E_Na)
        IK = g_K * n ** 4 * (V - E_K)
        IL = g_Leak * (V - E_Leak)
        dvdt = (- INa - IK - IL + Isyn) / C
        return dvdt

    def update(ST, _t):
        m = int_m(ST['m'], _t, ST['V'])
        h = int_h(ST['h'], _t, ST['V'])
        n = int_n(ST['n'], _t, ST['V'])
        V = int_V(ST['V'], _t, m, h, n, ST['inp'])
        sp = (ST['V'] < Vth) and (V >= Vth)
        ST['sp'] = sp
        ST['V'] = V
        ST['m'] = m
        ST['h'] = h
        ST['n'] = n
        ST['inp'] = Iext

    return bp.NeuType(name='HH_neuron',
                      ST=ST,
                      steps=update,
                      mode='scalar')


bp.profile.set(dt=0.1, numerical_method='exponential')


def hh_compare_cpu_and_multi_cpu(num=1000, vector=True):
    print(f'HH, vector_based={vector}, device=cpu', end=', ')
    bp.profile.set(jit=True, device='cpu')

    HH = define_hh()
    HH.mode = 'vector' if vector else 'scalar'
    neu = bp.NeuGroup(HH, geometry=num)

    t0 = time.time()
    neu.run(duration=1000., report=True)
    t_cpu = time.time() - t0
    print('used {:.3f} ms'.format(t_cpu))

    print(f'HH, vector_based={vector}, device=multi-cpu', end=', ')
    bp.profile.set(jit=True, device='multi-cpu')
    neu = bp.NeuGroup(HH, geometry=num)
    t0 = time.time()
    neu.run(duration=1000., report=True)
    t_multi_cpu = time.time() - t0
    print('used {:.3f} ms'.format(t_multi_cpu))

    print(f"HH model with multi-cpu speeds up {t_cpu / t_multi_cpu}")
    print()


def hh_compare_cpu_and_gpu(num=1000):
    print(f'HH, device=cpu', end=', ')
    bp.profile.set(jit=True, device='cpu', show_code=True)

    HH = define_hh()
    HH.mode = 'scalar'
    neu = bp.NeuGroup(HH, geometry=num)

    t0 = time.time()
    neu.run(duration=1000., report=True)
    t_cpu = time.time() - t0
    print('used {:.3f} ms'.format(t_cpu))

    print(f'HH, device=gpu', end=', ')
    bp.profile.set(jit=True, device='gpu')
    neu = bp.NeuGroup(HH, geometry=num)
    t0 = time.time()
    neu.run(duration=1000., report=True)
    t_multi_cpu = time.time() - t0
    print('used {:.3f} ms'.format(t_multi_cpu))

    print(f"HH model with multi-cpu speeds up {t_cpu / t_multi_cpu}")
    print()


if __name__ == '__main__':
    pass

    # hh_compare_cpu_and_multi_cpu(int(1e4))
    # hh_compare_cpu_and_multi_cpu(int(1e5))
    # hh_compare_cpu_and_multi_cpu(int(1e6))

    # hh_compare_cpu_and_gpu(int(1e4))
    # hh_compare_cpu_and_gpu(int(1e5))
    # hh_compare_cpu_and_gpu(int(1e6))
    # hh_compare_cpu_and_gpu(int(1e7))




