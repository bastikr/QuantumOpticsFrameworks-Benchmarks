using QuantumOptics
using BenchmarkTools
include("benchmarkutils.jl")

name = "timeevolution_schroedinger_jaynescummings"

samples = 3
evals = 3
cutoffs = [10:10:80;]

function setup(N)
    nothing
end

function f(N)
    ωa = 1
    ωc = 1
    g = 2
    tspan = [0:1:10;]

    b_cavity = FockBasis(N-1)
    b_atom = SpinBasis(1//2)
    b = b_cavity ⊗ b_atom

    a = destroy(b_cavity)
    at = create(b_cavity)
    n = number(b_cavity)

    sz = sigmaz(b_atom)
    sm = sigmam(b_atom)
    sp = sigmap(b_atom)

    H = embed(b, 1, ωc*n) + embed(b, 2, ωa*sz/2) + g*(at⊗sm+a⊗sp)
    ψ₀ = fockstate(b_cavity, 0) ⊗ normalize(spinup(b_atom) + spindown(b_atom))

    exp_n = Float64[]
    fout(t, ρ) = push!(exp_n, real(expect(1, n, ρ)))
    timeevolution.schroedinger(tspan, ψ₀, H; fout=fout, reltol=1e-6, abstol=1e-8)
    exp_n
end

println("Benchmarking: ", name)
print("Cutoff: ")
checks = Dict{Int, Float64}()
results = []
for N in cutoffs
    print(N, " ")
    checks[N] = sum(f(N))
    t = @belapsed f($N) samples=samples evals=evals
    push!(results, Dict("N"=>2*N, "t"=>t))
end
println()

benchmarkutils.check(name, checks)
benchmarkutils.save(name, results)
