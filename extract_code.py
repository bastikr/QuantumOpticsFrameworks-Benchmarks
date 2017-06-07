import os
import re
import subprocess

matlabbenchmarks = "benchmarks-QuantumOpticsToolbox"
juliabenchmarks = "benchmarks-QuantumOptics.jl"
pythonbenchmarks = "benchmarks-QuTiP"

outputdir = "sourcecode"

if not os.path.exists(outputdir):
    os.makedirs(outputdir)

template = """\

# ----------
# Setup code
# ----------
N = 2 # Hilbert space cutoff parameter
s = 0.1 # sparseness
{setupcode}

# --------------
# Benchmark code
# --------------
{benchmarkcode}
"""

template_julia = """\
using QuantumOptics
""" + template

template_python = """\
{imports}
""" + template

def read(path):
    f = open(path)
    text = f.read()
    f.close()
    return text

def write(name, text):
    outputpath = os.path.join(outputdir, name)
    f = open(outputpath, "w")
    f.write(text)
    f.close()

def extract_julia_function(text, name):
    start = text.find("\n", text.find("function " + name))
    end = text.find("\nend\n", start)
    code = text[start:end].replace("\n    ", "\n")[1:]
    return code

def extract_julia(path):
    text = read(path)
    return template_julia.format(
        setupcode = extract_julia_function(text, "setup").rsplit("\n", 1)[0],
        benchmarkcode = extract_julia_function(text, "f"))

def extract_python_function(text, name):
    start = text.find("\n", text.find("def " + name))
    end = text.find("\n", text.find("\n    return", start)+1)
    code = text[start:end].replace("\n    ", "\n")[1:]
    return code

def extract_python_imports(text):
    return list(filter(lambda x: x.startswith("import") and not "benchmarkutils" in x,
                    text.split("\n")))


def extract_python(path):
    text = read(path)
    imports = extract_python_imports(text)
    benchmarkcode = extract_python_function(text, "f")
    parts = benchmarkcode.rsplit("\n", 1)
    if len(parts) == 1:
        a = ""
        b = parts[0]
    else:
        a, b = parts
        a = a + "\n"
    benchmarkcode = a + b.replace("return ", "")
    return template_python.format(
        imports="\n".join(imports),
        setupcode=extract_python_function(text, "setup").rsplit("\n", 1)[0],
        benchmarkcode=benchmarkcode)

def testjulia(name):
    outputpath = os.path.join(outputdir, name)
    subprocess.run(["julia", outputpath], check=True)

def testpython(name):
    outputpath = os.path.join(outputdir, name)
    subprocess.run(["python3", outputpath], check=True)

# Extract QuantumOptics.jl source code
filenames = os.listdir(juliabenchmarks)
for name in filenames:
    if "benchmarkutils" in name or not name.endswith(".jl"):
        continue
    print("Extract: ", name)
    sourcecode = extract_julia(os.path.join(juliabenchmarks, name))
    write(name, sourcecode)
    # testjulia(name)


# Extract QuTiP source code
filenames = os.listdir(pythonbenchmarks)
for name in filenames:
    if "benchmarkutils" in name or not name.endswith(".py") or name=="__init__.py":
        continue
    print("Extract: ", name)
    sourcecode = extract_python(os.path.join(pythonbenchmarks, name))
    write(name, sourcecode)
    # testpython(name)
