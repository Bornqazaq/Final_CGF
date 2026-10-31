param([switch]$Test)
$ErrorActionPreference = 'Stop'
$projectRoot = [IO.Path]::GetFullPath((Join-Path $PSScriptRoot '..\..'))
$localCompiler = Join-Path $projectRoot '.tools\llvm\bin'
$localScripts = Join-Path $projectRoot '.tools\py\Scripts'
if (Test-Path -LiteralPath $localCompiler) { $env:PATH = "$localCompiler;$localScripts;$env:PATH" }
& cmake -S $projectRoot -B (Join-Path $projectRoot 'build') -G Ninja -DCMAKE_BUILD_TYPE=Release -DCMAKE_C_COMPILER=clang -DCMAKE_CXX_COMPILER=clang++
if ($LASTEXITCODE -ne 0) { throw 'CMake configure failed' }
& cmake --build (Join-Path $projectRoot 'build') --parallel 8
if ($LASTEXITCODE -ne 0) { throw 'Build failed' }
if ($Test) { & ctest --test-dir (Join-Path $projectRoot 'build') --output-on-failure; if ($LASTEXITCODE -ne 0) { throw 'Tests failed' } }
