#Requires -Version 5.1
<#
.SYNOPSIS
    Serve the Atlas site locally via Docker (ruby:3.3). Sidesteps Windows'
    260-char MAX_PATH limit that breaks native `bundle exec jekyll serve`
    on deeply-nested research artifacts.

.EXAMPLE
    .\serve.ps1
    # serves at http://localhost:4000/

.EXAMPLE
    .\serve.ps1 -Port 8080
    # serves at http://localhost:8080/

.EXAMPLE
    .\serve.ps1 -Baseurl /Atlas
    # serves at http://localhost:4000/Atlas/ — mirrors GitHub Pages exactly

.NOTES
    Default baseurl is empty so localhost paths work cleanly. Pass -Baseurl /Atlas
    if you want to mirror the production GH Pages URL shape during local testing.
#>
[CmdletBinding()]
param(
    [int]$Port = 4000,
    [string]$Baseurl = ""
)

$ErrorActionPreference = 'Stop'
Push-Location $PSScriptRoot

try {
    $rubyImage = 'ruby:3.3'
    $bundleVol = 'atlas-bundle'

    docker volume inspect $bundleVol *> $null
    if ($LASTEXITCODE -ne 0) {
        docker volume create $bundleVol | Out-Null
    }

    Write-Host "Installing gems (cached in volume '$bundleVol')..." -ForegroundColor Cyan
    docker run --rm `
        -v "${PWD}:/srv/jekyll" `
        -v "${bundleVol}:/usr/local/bundle" `
        -w /srv/jekyll `
        $rubyImage bundle install --quiet
    if ($LASTEXITCODE -ne 0) { throw "bundle install failed (exit $LASTEXITCODE)" }

    $url = if ($Baseurl) { "http://localhost:$Port$Baseurl/" } else { "http://localhost:$Port/" }
    Write-Host ""
    Write-Host "Serving $url  (Ctrl+C to stop)" -ForegroundColor Green
    Write-Host ""

    docker run --rm -it `
        -p "${Port}:4000" `
        -v "${PWD}:/srv/jekyll" `
        -v "${bundleVol}:/usr/local/bundle" `
        -w /srv/jekyll `
        $rubyImage bundle exec jekyll serve --host 0.0.0.0 --baseurl $Baseurl
}
finally {
    Pop-Location
}
