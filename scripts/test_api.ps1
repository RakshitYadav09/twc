$Base = 'http://127.0.0.1:8000'
Write-Output "Health:"
Invoke-RestMethod "$Base/health" | ConvertTo-Json -Depth 5

$body = @{ organization_name = 'smoketest'; email = 'smoke@example.com'; password = 'smoketest' } | ConvertTo-Json
Write-Output "Create org:"
Invoke-RestMethod -Method Post -Uri "$Base/org/create" -Body $body -ContentType 'application/json' | ConvertTo-Json -Depth 5
