Frontend:

Access to fetch at 'http://127.0.0.1:8000/api/v1/users/me' from origin 'http://localhost:3000' has been blocked by CORS policy: No 'Access-Control-Allow-Origin' header is present on the requested resource.Understand this error
client.ts:58  GET http://127.0.0.1:8000/api/v1/users/me net::ERR_FAILED 403 (Forbidden)
request @ client.ts:58
await in request
get @ client.ts:77
getMyProfile @ userService.ts:13
(anonymous) @ AuthContext.tsx:42
(anonymous) @ subscribe.ts:104
(anonymous) @ subscribe.ts:233
Promise.then
sendOne @ subscribe.ts:230
forEachObserver @ subscribe.ts:220
next @ subscribe.ts:103
notifyAuthListeners @ auth_impl.ts:710
(anonymous) @ auth_impl.ts:438
Promise.then
queue @ auth_impl.ts:790
_updateCurrentUser @ auth_impl.ts:436
await in _updateCurrentUser
_signInWithCredential @ credential.ts:56
await in _signInWithCredential
signInWithCredential @ credential.ts:79
signInWithEmailAndPassword @ email_and_password.ts:349
login @ AuthContext.tsx:93
handleSubmit @ Login.tsx:29
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
AuthContext.tsx:49 Failed to load user profile from backend: TypeError: Failed to fetch
    at APIClient.request (client.ts:58:1)
    at async Object.next (AuthContext.tsx:42:1)

Backend:
User profile not found for UID: uhhjERSGmvNMq0SpER0u2M1IWGp2
INFO:     127.0.0.1:64660 - "GET /api/v1/users/me HTTP/1.1" 403 Forbidden