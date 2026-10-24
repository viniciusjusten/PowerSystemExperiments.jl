import Pkg
Pkg.instantiate()

using Revise

# The dependencies of PowerFlow load Distributed, which triggers an extension of Revise. The environment of Revise
# stays in the load path after the package is activated, so that the extension is still found
push!(LOAD_PATH, @__DIR__)

Pkg.activate(dirname(@__DIR__))
Pkg.instantiate()

using PowerSystemExperiments
