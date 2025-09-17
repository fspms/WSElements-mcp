# PowerShell startup script for WithSecure Elements MCP Server

param(
    [string]$Transport = "stdio",
    [string]$Host = "localhost",
    [int]$Port = 8000,
    [string]$Modules = "incidents,events,organizations,devices"
)

# Function to display messages
function Write-Message {
    param([string]$Message, [string]$Color = "Blue")
    Write-Host "[WithSecure Elements MCP] $Message" -ForegroundColor $Color
}

function Write-Success {
    param([string]$Message)
    Write-Host "[WithSecure Elements MCP] $Message" -ForegroundColor Green
}

function Write-Warning {
    param([string]$Message)
    Write-Host "[WithSecure Elements MCP] $Message" -ForegroundColor Yellow
}

function Write-Error {
    param([string]$Message)
    Write-Host "[WithSecure Elements MCP] $Message" -ForegroundColor Red
}

# Check if .env file exists
if (-not (Test-Path ".env")) {
    Write-Warning ".env file not found. Creating from env.example..."
    if (Test-Path "env.example") {
        Copy-Item "env.example" ".env"
        Write-Warning "Please edit .env file with your WithSecure Elements information"
        exit 1
    } else {
        Write-Error "env.example file not found"
        exit 1
    }
}

# Load environment variables
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^#][^=]+)=(.*)$") {
        [Environment]::SetEnvironmentVariable($matches[1], $matches[2], "Process")
    }
}

# Check required environment variables
$ClientId = [Environment]::GetEnvironmentVariable("WITHSECURE_CLIENT_ID")
$ClientSecret = [Environment]::GetEnvironmentVariable("WITHSECURE_CLIENT_SECRET")

if (-not $ClientId -or -not $ClientSecret) {
    Write-Error "WITHSECURE_CLIENT_ID and WITHSECURE_CLIENT_SECRET must be defined in .env"
    exit 1
}

Write-Message "Starting WithSecure Elements MCP server..."
Write-Message "Transport: $Transport"
Write-Message "Host: $Host"
Write-Message "Port: $Port"
Write-Message "Modules: $Modules"

# Build arguments
$Args = @("--transport", $Transport)

if ($Transport -ne "stdio") {
    $Args += @("--host", $Host, "--port", $Port)
}

if ($Modules) {
    $Args += @("--modules", $Modules)
}

# Start server
Write-Success "Launching server..."
& withsecure-elements-mcp @Args
