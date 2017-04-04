using QuantumOptics
using BenchmarkTools
include("benchmarkutils.jl")

name = "fft-timeevolution_particle"

samples = 3
evals = 3
cutoffs = [100:100:1200;]

xmin = -10
xmax = 10

x0 = 2
p0 = 1
sigma0 = 1

function setup(Npoints)
    bx = PositionBasis(xmin, xmax, Npoints)
    bp = MomentumBasis(bx)
    x = position(bx)
    p = momentum(bp)
    Tpx = FFTOperator(bp, bx)
    Txp = dagger(Tpx)
    H = LazySum(LazyProduct(Txp, p^2, Tpx), 2*x^2)
    psi0 = gaussianstate(bx, x0, p0, sigma0)
    (psi0, H, x)
end

function f(psi0, H, x)
    T = [0:0.1:1;]
    exp_x = Float64[]
    fout(t, psi) = push!(exp_x, real(expect(x, psi)))
    timeevolution.schroedinger(T, psi0, H; fout=fout, reltol=1e-6, abstol=1e-6)
    exp_x
end

println("Benchmarking: ", name)
print("Cutoff: ")
checks = Dict{Int, Float64}()
results = []
for N in cutoffs
    print(N, " ")
    psi0, H, x = setup(N)
    checks[N] = abs(sum(f(psi0, H, x)))
    t = @belapsed f($psi0, $H, $x) samples=samples evals=evals
    push!(results, Dict("N"=>N, "t"=>t))
end
println()

benchmarkutils.check(name, checks)
benchmarkutils.save(name, results)
