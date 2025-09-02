File selected: Template Carta Instrucción Banco ABC (Compensación).docx Type: application/vnd.openxmlformats-officedocument.wordprocessingml.document
BankDashboard.tsx:615 Save - uploadedFile: Template Carta Instrucción Banco ABC (Compensación).docx
BankDashboard.tsx:618 Taking WITH document path
client.ts:119  POST http://127.0.0.1:8000/api/v1/banks/banco-abc/settlement-letters/with-document 400 (Bad Request)
postFormData @ client.ts:119
await in postFormData
createSettlementLetterWithDocument @ bankService.ts:248
handleSaveLetter @ BankDashboard.tsx:632
callCallback @ react-dom.development.js:4164
invokeGuardedCallbackDev @ react-dom.development.js:4213
invokeGuardedCallback @ react-dom.development.js:4277
invokeGuardedCallbackAndCatchFirstError @ react-dom.development.js:4291
executeDispatch @ react-dom.development.js:9041
processDispatchQueueItemsInOrder @ react-dom.development.js:9073
processDispatchQueue @ react-dom.development.js:9086
dispatchEventsForPlugins @ react-dom.development.js:9097
(anonymous) @ react-dom.development.js:9288
batchedUpdates$1 @ react-dom.development.js:26179
batchedUpdates @ react-dom.development.js:3991
dispatchEventForPluginEventSystem @ react-dom.development.js:9287
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ react-dom.development.js:6465
dispatchEvent @ react-dom.development.js:6457
dispatchDiscreteEvent @ react-dom.development.js:6430Understand this error
BankDashboard.tsx:702 Error saving settlement letter: Error: Request failed: 400
    at APIClient.postFormData (client.ts:129:1)
    at async handleSaveLetter (BankDashboard.tsx:632:1)
handleSaveLetter @ BankDashboard.tsx:702
await in handleSaveLetter
callCallback @ react-dom.development.js:4164
invokeGuardedCallbackDev @ react-dom.development.js:4213
invokeGuardedCallback @ react-dom.development.js:4277
invokeGuardedCallbackAndCatchFirstError @ react-dom.development.js:4291
executeDispatch @ react-dom.development.js:9041
processDispatchQueueItemsInOrder @ react-dom.development.js:9073
processDispatchQueue @ react-dom.development.js:9086
dispatchEventsForPlugins @ react-dom.development.js:9097
(anonymous) @ react-dom.development.js:9288
batchedUpdates$1 @ react-dom.development.js:26179
batchedUpdates @ react-dom.development.js:3991
dispatchEventForPluginEventSystem @ react-dom.development.js:9287
dispatchEventWithEnableCapturePhaseSelectiveHydrationWithoutDiscreteEventReplay @ react-dom.development.js:6465
dispatchEvent @ react-dom.development.js:6457
dispatchDiscreteEvent @ react-dom.development.js:6430


BACKEND:
2025-09-02 17:34:32,736 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-09-02 17:34:32,740 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-09-02 17:34:32,741 - cachecontrol.controller - DEBUG - Current age based on date: 353
2025-09-02 17:34:32,741 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 24636
2025-09-02 17:34:32,741 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-09-02 17:34:32,741 - cachecontrol.controller - DEBUG - 24636 > 353
2025-09-02 17:34:32,960 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-09-02 17:34:33,018 - api.middleware.auth_middleware - INFO - Authenticated user: admin@bancoabc.cl (uhhjERSGmvNMq0SpER0u2M1IWGp2)
2025-09-02 17:34:33,020 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,020 - multipart.multipart - DEBUG - Calling on_header_field with data[42:61]
2025-09-02 17:34:33,020 - multipart.multipart - DEBUG - Calling on_header_value with data[63:90]
2025-09-02 17:34:33,020 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,021 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,021 - multipart.multipart - DEBUG - Calling on_part_data with data[94:100]
2025-09-02 17:34:33,021 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,021 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,022 - multipart.multipart - DEBUG - Calling on_header_field with data[144:163]
2025-09-02 17:34:33,022 - multipart.multipart - DEBUG - Calling on_header_value with data[165:190]
2025-09-02 17:34:33,022 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,022 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_part_data with data[194:201]
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_header_field with data[245:264]
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_header_value with data[266:299]
2025-09-02 17:34:33,023 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,024 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,024 - multipart.multipart - DEBUG - Calling on_part_data with data[303:316]
2025-09-02 17:34:33,024 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,025 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,025 - multipart.multipart - DEBUG - Calling on_header_field with data[360:379]
2025-09-02 17:34:33,025 - multipart.multipart - DEBUG - Calling on_header_value with data[381:407]
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_part_data with data[411:412]
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,026 - multipart.multipart - DEBUG - Calling on_header_field with data[456:475]
2025-09-02 17:34:33,027 - multipart.multipart - DEBUG - Calling on_header_value with data[477:501]
2025-09-02 17:34:33,027 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,027 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,027 - multipart.multipart - DEBUG - Calling on_part_data with data[505:509]
2025-09-02 17:34:33,027 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,028 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,028 - multipart.multipart - DEBUG - Calling on_header_field with data[553:572]
2025-09-02 17:34:33,028 - multipart.multipart - DEBUG - Calling on_header_value with data[574:610]
2025-09-02 17:34:33,028 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,028 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_part_data with data[614:616]
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_header_field with data[660:679]
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_header_value with data[681:709]
2025-09-02 17:34:33,029 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,030 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,030 - multipart.multipart - DEBUG - Calling on_part_data with data[713:715]
2025-09-02 17:34:33,030 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,030 - multipart.multipart - DEBUG - Calling on_part_begin with no data
2025-09-02 17:34:33,030 - multipart.multipart - DEBUG - Calling on_header_field with data[759:778]
2025-09-02 17:34:33,031 - multipart.multipart - DEBUG - Calling on_header_value with data[780:877]
2025-09-02 17:34:33,031 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,031 - multipart.multipart - DEBUG - Calling on_header_field with data[879:891]
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_header_value with data[893:964]
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_header_end with no data
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_headers_finished with no data
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_part_data with data[968:23013]
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_part_end with no data
2025-09-02 17:34:33,032 - multipart.multipart - DEBUG - Calling on_end with no data
2025-09-02 17:34:33,033 - config.storage_config - INFO - Attempting to use Application Default Credentials
2025-09-02 17:34:33,034 - google.auth._default - DEBUG - Checking None for explicit credentials as part of auth process...
2025-09-02 17:34:33,034 - google.auth._default - DEBUG - Checking Cloud SDK credentials as part of auth process...
2025-09-02 17:34:34,247 - urllib3.util.retry - DEBUG - Converted retries value: 3 -> Retry(total=3, connect=None, read=None, redirect=None, status=None)
2025-09-02 17:34:34,248 - google.auth.transport.requests - DEBUG - Making request: POST https://oauth2.googleapis.com/token
2025-09-02 17:34:34,249 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): oauth2.googleapis.com:443
2025-09-02 17:34:34,295 - urllib3.connectionpool - DEBUG - https://oauth2.googleapis.com:443 "POST /token HTTP/1.1" 200 None
2025-09-02 17:34:34,297 - urllib3.connectionpool - DEBUG - Starting new HTTPS connection (1): storage.googleapis.com:443
2025-09-02 17:34:34,563 - urllib3.connectionpool - DEBUG - https://storage.googleapis.com:443 "GET /storage/v1/b?maxResults=1&project=ccm-dev-pool&projection=noAcl&prettyPrint=false HTTP/1.1" 200 969
2025-09-02 17:34:34,564 - config.storage_config - INFO - Storage client initialized for project: ccm-dev-pool
INFO:     127.0.0.1:63696 - "POST /api/v1/banks/banco-abc/settlement-letters/with-document HTTP/1.1" 400 Bad Request