using QuantumOptics
using BenchmarkTools
include("benchmarkutils.jl")

name = "timeevolution_schroedinger_particle[fft]"

samples = 3
evals = 1
cutoffs = [50:50:200;]

function setup(N)
    xmin = -5
    xmax = 5
    x0 = 0.3
    p0 = -0.2
    sigma0 = 1
    bx = PositionBasis(xmin, xmax, N)
    bp = MomentumBasis(bx)
    x = position(bx)
    p = momentum(bp)
    Tpx = transform(bp, bx)
    Txp = dagger(Tpx)
    H = LazySum(LazyProduct(Txp, p^2, Tpx), 2*x^2)
    psi0 = gaussianstate(bx, x0, p0, sigma0)
    psi0, H, x
end

function f(psi0, H, x)
    T = [0:1.:10;]
    exp_x = Float64[]
    fout(t, psi) = push!(exp_x, real(expect(x, psi)))
    timeevolution.schroedinger(T, psi0, H; fout=fout, reltol=1e-6, abstol=1e-8)
    exp_x
end

println("Benchmarking: ", name)
print("Cutoff: ")
checks = Dict{Int, Float64}()
results = []
for N in cutoffs
    print(N, " ")
    psi0, H, x = setup(N)
    checks[N] = sum(f(psi0, H, x))
    t = @belapsed f($psi0, $H, $x) samples=samples evals=evals
    push!(results, Dict("N"=>N, "t"=>t))
end
println()

benchmarkutils.check(name, checks)
benchmarkutils.save(name, results)
