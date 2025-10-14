2025-10-14 10:44:04,364 - services.client_service - INFO - ✅ Successfully created match with ID: 6QI0TWbPfGvNYxwTVXK2 in collection clients/xyz-corp/matches
2025-10-14 10:44:04,567 - services.client_service - INFO - ✅ Added match_id 0e4812d4-884a-45cb-8684-58be415f4ce9 and status 'Difference' to trade BCI00002 in email 7o0Fq8GyqnjlO5vSnr8Y
2025-10-14 10:44:04,629 - services.client_service - INFO - Successfully updated email 7o0Fq8GyqnjlO5vSnr8Y trade BCI00002 with match_id 0e4812d4-884a-45cb-8684-58be415f4ce9 and status 'Difference'
2025-10-14 10:44:04,680 - services.client_service - INFO - Trade has 1 differences - checking dispute email automation
2025-10-14 10:44:04,680 - services.client_service - INFO - Email automation disabled for dispute emails in client xyz-corp
2025-10-14 10:44:04,680 - services.client_service - INFO - Created match between trade NAa2XRjCxFJrkxFHIKqi and email 7o0Fq8GyqnjlO5vSnr8Y with 100% confidence
2025-10-14 10:44:04,680 - services.client_service - INFO - ✅ Successfully created match for trade 32011 with 100% confidence
2025-10-14 10:44:04,681 - services.client_service - INFO - Email processing complete for email_body_Ben Clark <ben.clark.txt: 1 matches, 0 duplicates
2025-10-14 10:44:04,681 - services.event_service - INFO - 📡 Broadcasting event gmail_processed to 1 subscription groups
2025-10-14 10:44:04,681 - services.event_service - DEBUG - 📡 Checking subscription group xyz-corp:D5HgqZfogqM3FyyH3zeJdu2Gt1F2 with 2 connections
2025-10-14 10:44:04,682 - services.event_service - DEBUG -    - PASSED all checks
2025-10-14 10:44:04,682 - services.event_service - DEBUG - 📡 Event gmail_processed matches subscription fdebda44-bbaf-4502-b922-bc2a9a0234c9: True
2025-10-14 10:44:04,682 - services.event_service - DEBUG -    - Event client_id: xyz-corp, Subscription client_id: xyz-corp
2025-10-14 10:44:04,682 - services.event_service - DEBUG -    - Event user_id: None, Subscription user_id: D5HgqZfogqM3FyyH3zeJdu2Gt1F2
2025-10-14 10:44:04,682 - services.event_service - DEBUG -    - Event type: gmail_processed, Subscription types: ['gmail_processed']
2025-10-14 10:44:04,682 - services.event_service - DEBUG -    - Event priority: medium, Subscription priority_filter: None
2025-10-14 10:44:04,683 - services.event_service - INFO - 📡 Event queued for connection fdebda44-bbaf-4502-b922-bc2a9a0234c9
2025-10-14 10:44:04,683 - services.event_service - DEBUG -    - PASSED all checks
2025-10-14 10:44:04,683 - services.event_service - DEBUG - 📡 Event gmail_processed matches subscription 505a3741-ca2a-4170-8d3d-8aa85269a126: True
2025-10-14 10:44:04,683 - services.event_service - DEBUG -    - Event client_id: xyz-corp, Subscription client_id: xyz-corp
2025-10-14 10:44:04,683 - services.event_service - DEBUG -    - Event user_id: None, Subscription user_id: D5HgqZfogqM3FyyH3zeJdu2Gt1F2
2025-10-14 10:44:04,683 - services.event_service - DEBUG -    - Event type: gmail_processed, Subscription types: ['gmail_processed']
2025-10-14 10:44:04,684 - services.event_service - DEBUG -    - Event priority: medium, Subscription priority_filter: None
2025-10-14 10:44:04,684 - services.event_service - INFO - 📡 Event queued for connection 505a3741-ca2a-4170-8d3d-8aa85269a126
2025-10-14 10:44:04,684 - services.event_service - INFO - 📡 Emitted event: gmail_processed - Email Processed Successfully (client: xyz-corp, priority: medium)
2025-10-14 10:44:04,684 - services.client_service - INFO - 📡 Emitted Gmail processing event: Email Processed Successfully
2025-10-14 10:44:04,684 - services.client_service - INFO - ✅ Gmail body processing completed: {'email_id': '7o0Fq8GyqnjlO5vSnr8Y', 'trades_extracted': 1, 'confirmation_detected': True, 'processed_at': '2025-10-14T10:44:04.097242', 'matches_found': 1, 'matched_trade_numbers': ['32011'], 'duplicates_found': 0, 'counterparty_name': 'Bci', 'matching_attempted': True, 'processing_complete': True}
2025-10-14 10:44:04,685 - services.gmail_service - INFO - ✅ Successfully processed email body from Ben Clark <ben.clark@palace.cl>
2025-10-14 10:44:04,685 - services.gmail_service - INFO - Successfully processed message 199e2f63b63f3359: 1 trades extracted
2025-10-14 10:44:04,685 - services.gmail_service - INFO - ✅ Processed 1 emails in check #3
2025-10-14 10:44:04,685 - services.gmail_service - INFO - 📊 Email from Ben Clark <ben.clark@palace.cl>: 1 trades, 1 matches, 0 duplicates
2025-10-14 10:44:04,685 - services.gmail_service - DEBUG - ⏰ Waiting 30s until next check...
2025-10-14 10:44:04,686 - api.routes.events - INFO - 📡 Received event: gmail_processed - Email Processed Successfully
2025-10-14 10:44:04,686 - api.routes.events - INFO - 📡 Received event: gmail_processed - Email Processed Successfully
2025-10-14 10:44:05,191 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-10-14 10:44:05,191 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-10-14 10:44:05,192 - cachecontrol.controller - DEBUG - Current age based on date: 84
2025-10-14 10:44:05,192 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 20129
2025-10-14 10:44:05,192 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-10-14 10:44:05,192 - cachecontrol.controller - DEBUG - 20129 > 84
2025-10-14 10:44:05,429 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-10-14 10:44:05,662 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-10-14 10:44:05,663 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-10-14 10:44:05,664 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-10-14 10:44:05,664 - cachecontrol.controller - DEBUG - Current age based on date: 84
2025-10-14 10:44:05,664 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 20129
2025-10-14 10:44:05,665 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-10-14 10:44:05,665 - cachecontrol.controller - DEBUG - 20129 > 84
2025-10-14 10:44:05,958 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-10-14 10:44:06,194 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-10-14 10:44:06,353 - services.client_service - INFO - Retrieved 1 trade records from email confirmations for client xyz-corp
2025-10-14 10:44:06,487 - services.client_service - INFO - Trade differences found (1 fields): Price: 932.32 vs 932.33
2025-10-14 10:44:06,488 - services.client_service - INFO - Retrieved 1 matched trades for client xyz-corp
2025-10-14 10:44:06,489 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-10-14 10:44:06,490 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-10-14 10:44:06,490 - cachecontrol.controller - DEBUG - Current age based on date: 85
2025-10-14 10:44:06,490 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 20129
2025-10-14 10:44:06,491 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-10-14 10:44:06,491 - cachecontrol.controller - DEBUG - 20129 > 85
2025-10-14 10:44:06,815 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-10-14 10:44:07,082 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-10-14 10:44:07,136 - services.client_service - INFO - Retrieved 10 total trades for client xyz-corp
INFO:     None:0 - "GET /api/v1/clients/xyz-corp/all-email-confirmations HTTP/1.1" 200 OK
INFO:     None:0 - "GET /api/v1/clients/xyz-corp/matched-trades HTTP/1.1" 200 OK
INFO:     None:0 - "GET /api/v1/clients/xyz-corp/unmatched-trades HTTP/1.1" 200 OK
2025-10-14 10:44:07,454 - google.auth.transport.requests - DEBUG - Making request: GET https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com
2025-10-14 10:44:07,456 - cachecontrol.controller - DEBUG - Looking up "https://www.googleapis.com/robot/v1/metadata/x509/securetoken@system.gserviceaccount.com" in the cache
2025-10-14 10:44:07,457 - cachecontrol.controller - DEBUG - Current age based on date: 86
2025-10-14 10:44:07,457 - cachecontrol.controller - DEBUG - Freshness lifetime from max-age: 20129
2025-10-14 10:44:07,457 - cachecontrol.controller - DEBUG - The response is "fresh", returning cached response
2025-10-14 10:44:07,457 - cachecontrol.controller - DEBUG - 20129 > 86
2025-10-14 10:44:07,792 - urllib3.connectionpool - DEBUG - https://identitytoolkit.googleapis.com:443 "POST /v1/projects/ccm-dev-pool/accounts:lookup HTTP/1.1" 200 None
2025-10-14 10:44:08,065 - api.middleware.auth_middleware - INFO - Authenticated user: admin@xyz.cl (D5HgqZfogqM3FyyH3zeJdu2Gt1F2)
2025-10-14 10:44:08,242 - services.client_service - INFO - Trade differences found (1 fields): Price: 932.32 vs 932.33
2025-10-14 10:44:08,243 - services.client_service - INFO - Retrieved 1 matched trades for client xyz-corp
INFO:     None:0 - "GET /api/v1/clients/xyz-corp/matched-trades HTTP/1.1" 200 OK
2025-10-14 10:44:34,686 - services.gmail_service - INFO - 🔍 Gmail check #4 - Monitoring confirmaciones_dev@servicios.palace.cl...
2025-10-14 10:44:34,687 - googleapiclient.discovery - DEBUG - URL being requested: GET https://gmail.googleapis.com/gmail/v1/users/me/history?startHistoryId=37720&alt=json
2025-10-14 10:44:34,688 - api.routes.events - DEBUG - 📡 Sending heartbeat for connection fdebda44-bbaf-4502-b922-bc2a9a0234c9
2025-10-14 10:44:34,688 - api.routes.events - DEBUG - 📡 Sending heartbeat for connection 505a3741-ca2a-4170-8d3d-8aa85269a126
2025-10-14 10:44:34,897 - services.gmail_service - DEBUG - No new emails found
2025-10-14 10:44:34,897 - services.gmail_service - DEBUG - 🔄 No new emails found in check #4
2025-10-14 10:44:34,898 - services.gmail_service - DEBUG - ⏰ Waiting 30s until next check...
2025-10-14 10:45:04,686 - api.routes.events - DEBUG - 📡 Sending heartbeat for connection 505a3741-ca2a-4170-8d3d-8aa85269a126
2025-10-14 10:45:04,687 - api.routes.events - DEBUG - 📡 Sending heartbeat for connection fdebda44-bbaf-4502-b922-bc2a9a0234c9
2025-10-14 10:45:04,901 - services.gmail_service - INFO - 🔍 Gmail check #5 - Monitoring confirmaciones_dev@servicios.palace.cl...
2025-10-14 10:45:04,902 - googleapiclient.discovery - DEBUG - URL being requested: GET https://gmail.googleapis.com/gmail/v1/users/me/history?startHistoryId=37720&alt=json
2025-10-14 10:45:05,089 - services.gmail_service - DEBUG - No new emails found
2025-10-14 10:45:05,089 - services.gmail_service - DEBUG - 🔄 No new emails found in check #5
2025-10-14 10:45:05,089 - services.gmail_service - DEBUG - ⏰ Waiting 30s until next check...