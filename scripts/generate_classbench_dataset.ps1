param(
  [string]$Seed = "..\parameter_files\acl1_seed",
  [int]$Rules = 100000,
  [string]$Output = "..\..\data\classbench\acl1_100000.txt"
)

$ErrorActionPreference = "Stop"
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$generatorDir = Resolve-Path (Join-Path $scriptDir "..\external\classbench-packet-classification\db_generator")
Push-Location $generatorDir
try {
  if (!(Test-Path ".\db_generator.exe") -and !(Test-Path ".\db_generator")) {
    make
  }
  $exe = if (Test-Path ".\db_generator.exe") { ".\db_generator.exe" } else { ".\db_generator" }
  & $exe -bc $Seed $Rules 2 0.5 -0.1 $Output
}
finally {
  Pop-Location
}
