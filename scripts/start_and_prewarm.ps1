$env:LOG_TELEMETRY="true"; $env:OPENBLAS_NUM_THREADS="1"; $env:OMP_NUM_THREADS="1"
Start-Process powershell -ArgumentList 'python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --log-level warning --no-access-log' -WindowStyle Minimized
Start-Sleep -Seconds 2
$u=@(
 "http://127.0.0.1:8000/ask?q=safety%20signals&k=5",
 "http://127.0.0.1:8000/ask?q=market%20access&k=5",
 "http://127.0.0.1:8000/ask?q=policy%20compliance&k=5"
); foreach($x in $u){curl.exe -s $x > $null}
