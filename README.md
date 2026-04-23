Started by upstream project "pipeline" build number 
7
originally caused by:
 Started by user 
admin
Running as SYSTEM
Building in workspace /var/lib/jenkins/workspace/healthy
[healthy] $ /bin/sh -xe /tmp/jenkins17295337174044151331.sh
+ curl 
http://127.0.0.1:5003/invocations -HContent-Type:application/json --data { "inputs": [[3.5, 25.0, 5.5, 1.0, 500.0, 2.5, 34.5, -118.5]] }
  % Total    % Received % Xferd  Average Speed   Time    Time     Time  Current
                                 Dload  Upload   Total   Spent    Left  Speed

  0     0    0     0    0     0      0      0 --:--:-- --:--:-- --:--:--     0
100   420  100   357  100    63   151k  27462 --:--:-- --:--:-- --:--:--  205k
{"error_code": "INVALID_PARAMETER_VALUE", "message": "Failed to predict data '[[   3.5   25.     5.5    1.   500.     2.5   34.5 -118.5]]'. \nError: Failed to enforce schema of data '[[   3.5   25.     5.5    1.   500.     2.5   34.5 -118.5]]' with schema '[Tensor('float64', (-1, 9))]'. Error: Shape of input (1, 8) does not match expected shape (-1, 9)."}Finished: SUCCESS
