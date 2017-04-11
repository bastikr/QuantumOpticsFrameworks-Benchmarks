import sys
print(sys.path)
import qutip as qt
import numpy as np
import benchmarkutils

name = "cython-timeevolution_timedependent"

samples = 3
evals = 1
cutoffs = range(10, 151, 10)

options = qt.Options()
options.num_cpus = 1
options.nsteps = 1000000
options.atol = 1e-8
options.rtol = 1e-6

# System parameters
omega = 1.89  # Frequency of driving laser
omega_c = 2.13  # Cavity frequency
eta = 0.76  # Pump strength
kappa = 0.34  # Decay rate

def f(Ncutoff):
    a = qt.destroy(Ncutoff)
    at = qt.create(Ncutoff)
    n = qt.num(Ncutoff)

    J = [np.sqrt(kappa)*a]

    # Initial state
    alpha0 = 0.3 - 0.5j
    psi0 = qt.coherent(Ncutoff, alpha0)

    tlist = np.linspace(0, 10., 11)
    H = [omega_c*n,
            [eta*a, 'exp(1j*1.89*t)'],
            [eta*at, 'np.exp(-1j*1.89*t)']]
    alpha_t = np.real(qt.mesolve(H, psi0, tlist, J, [a], options=options).expect[0])
    return alpha_t


print("Benchmarking:", name)
print("Cutoff: ", end="", flush=True)
checks = {}
results = []
for N in cutoffs:
    print(N, "", end="", flush=True)
    checks[N] = sum(f(N))
    t = benchmarkutils.run_benchmark(f, N, samples=samples, evals=evals)
    results.append({"N": N, "t": t})
print()

benchmarkutils.check(name.replace("cython-", ""), checks, 1e-4)
benchmarkutils.save(name, results)