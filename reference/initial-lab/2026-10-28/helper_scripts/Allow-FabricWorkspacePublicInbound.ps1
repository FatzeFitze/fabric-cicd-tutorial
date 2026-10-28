param(
    [Parameter(Mandatory = $true)]
    [guid] $WorkspaceId
)

$ErrorActionPreference = 'Stop'
$tenantId = '00000000-0000-0000-0000-000000000001'
$uri = "https://api.fabric.microsoft.com/v1/workspaces/$WorkspaceId/networking/communicationPolicy"

$token = az account get-access-token --tenant $tenantId --resource https://api.fabric.microsoft.com --query accessToken -o tsv
if ($LASTEXITCODE -ne 0 -or -not $token) { throw 'Could not obtain a Fabric token from the active az login session.' }
$headers = @{ Authorization = "Bearer $token" }

# GET first: PUT replaces the policy, including its outbound setting.
$current = Invoke-WebRequest -Uri $uri -Method Get -Headers $headers -UseBasicParsing
$policy = $current.Content | ConvertFrom-Json
if (-not $policy.inbound.publicAccessRules -or -not $policy.outbound.publicAccessRules.defaultAction) {
    throw 'The current policy is incomplete; refusing to overwrite it.'
}
$policy.inbound.publicAccessRules.defaultAction = 'Allow'

$etag = [string] $current.Headers['ETag']
if (-not $etag) { throw 'GET did not return an ETag; refusing to overwrite the policy.' }
if (-not $etag.StartsWith('"')) { $etag = '"' + $etag + '"' }
$headers['If-Match'] = $etag

Invoke-WebRequest -Uri $uri -Method Put -Headers $headers -ContentType 'application/json' `
    -Body ($policy | ConvertTo-Json -Depth 20 -Compress) -UseBasicParsing | Out-Null

$updated = Invoke-RestMethod -Uri $uri -Method Get -Headers @{ Authorization = "Bearer $token" }
Write-Host "Workspace $WorkspaceId inbound public access: $($updated.inbound.publicAccessRules.defaultAction)"
