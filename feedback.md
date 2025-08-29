2025-08-29 10:53:12,041 - services.client_service - INFO - Retrieved 1 matched trades for client xyz-corp
2025-08-29 10:53:12,041 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-08-29 10:53:12,042 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-08-29 10:53:12,043 - cachecontrol.controller - DEBUG - Current age based on date: 19
2025-08-29 10:53:12,043 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 19452
2025-08-29 10:53:12,043 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-08-29 10:53:12,043 - cachecontrol.controller - DEBUG - 19452 > 19
2025-08-29 10:53:12,270 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-08-29 10:53:12,339 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-08-29 10:53:12,396 - services.client_service - INFO - Retrieved 1 trade records from email confirmations for client xyz-corp
2025-08-29 10:53:12,399 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-08-29 10:53:12,400 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-08-29 10:53:12,400 - cachecontrol.controller - DEBUG - Current age based on date: 19
2025-08-29 10:53:12,401 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 19452
2025-08-29 10:53:12,401 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-08-29 10:53:12,401 - cachecontrol.controller - DEBUG - 19452 > 19
2025-08-29 10:53:12,569 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-08-29 10:53:12,656 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-08-29 10:53:12,675 - services.client_service - INFO - Retrieved 10 total trades for client xyz-corp
2025-08-29 10:53:12,676 - services.gmail_service - ERROR - ❌ Failed to send email to Estimados señores,
Se ha negociado entre Bci y XYZ Corp la siguiente operación de monedas:
1. Tipo de Operación:   Seguro de Cambio
2. Operador:    Juan Pérez
3. Moneda Extranjera de Referencia:     USD
4. Cantidad Moneda Extranjera de Referencia:    330.000,00
5. Comprador de Seguro de Cambio:       XYZ Corp
6. Vendedor de Seguro de Cambio:        Bci
7. Modalidad de Cumplimiento:   Compensación
8. Moneda Compensación: CLP
9. Fecha de Cierre Operación:   1 octubre 2025
10. Fecha de Vigencia Operación:        1 octubre 2025
11. Fecha de Vencimiento:       1 octubre 2026
12. Fecha Valuta de Pago:       3 octubre 2026
13. Plazo:      366 días
14. Precio Forward:     932,35
15. Paridad Referencial de Salida:      USD OBSERVADO
16. Fecha de Vigencia:  1 octubre 2026
17. Forma de Pago Cliente:      SWIFT
18. Forma de Pago Banco ABC:    Cuenta Corriente
19. Observaciones:
En señal de conformidad de las condiciones arriba señaladas, agradecemos enviar una copia firmada de esta confirmación al e-mail confirmacionesderivados@bancoabc.cl o bien responder el presente correo, entregando vuestra conformidad.
Atentamente,
Bci
: <HttpError 400 when requesting https://gmail.googleapis.com/gmail/v1/users/me/messages/send?alt=json returned "Invalid To header". Details: "[{'message': 'Invalid To header', 'domain': 'global', 'reason': 'invalidArgument'}]">
Traceback (most recent call last):
  File "C:\Users\bencl\Proyectos\ccm2.0\backend\src\services\gmail_service.py", line 716, in send_email
    result = await self._execute_gmail_api(
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\bencl\Proyectos\ccm2.0\backend\src\services\gmail_service.py", line 149, in _execute_gmail_api
    return await loop.run_in_executor(self.executor, request.execute)
           ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\bencl\AppData\Local\Programs\Python\Python311\Lib\concurrent\futures\thread.py", line 58, in run
    result = self.fn(*self.args, **self.kwargs)
             ^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\bencl\Proyectos\ccm2.0\backend\venv\Lib\site-packages\googleapiclient\_helpers.py", line 130, in positional_wrapper
    return wrapped(*args, **kwargs)
           ^^^^^^^^^^^^^^^^^^^^^^^^
  File "C:\Users\bencl\Proyectos\ccm2.0\backend\venv\Lib\site-packages\googleapiclient\http.py", line 938, in execute
    raise HttpError(resp, content, uri=self.uri)
googleapiclient.errors.HttpError: <HttpError 400 when requesting https://gmail.googleapis.com/gmail/v1/users/me/messages/send?alt=json returned "Invalid To header". Details: "[{'message': 'Invalid To header', 'domain': 'global', 'reason': 'invalidArgument'}]">
2025-08-29 10:53:12,679 - api.routes.internal_tasks - ERROR - ❌ Email task email_confirmation_1756479189_4450 failed to send email
INFO:     None:0 - "GET /api/v1/clients/xyz-corp/matched-trades HTTP/1.1" 200 OK