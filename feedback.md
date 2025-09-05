{
insertId: "pu08t2d3phz"
jsonPayload: {
@type: "type.googleapis.com/google.cloud.tasks.logging.v1.TaskActivityLog"
attemptResponseLog: {
attemptDuration: "0.001250s"
dispatchCount: "1"
maxAttempts: 0
responseCount: "0"
retryTime: "2025-09-05T20:39:23.111491Z"
scheduleTime: "2025-09-05T20:38:23.096373Z"
status: "UNKNOWN"
targetAddress: "POST http://localhost:8000/api/internal/tasks/email"
targetType: "HTTP"
}
task: "projects/ccm-dev-pool/locations/us-east4/queues/email-tasks/tasks/061918363491882526"
}
labels: {
}
logName: "projects/ccm-dev-pool/logs/cloudtasks.googleapis.com%2Ftask_operations_log"
payload: "jsonPayload"
receiveLocation: "us-east4"
receiveTimestamp: "2025-09-05T20:38:23.901407306Z"
resource: {
labels: {4}
type: "cloud_tasks_queue"
}
severity: "ERROR"
timestamp: "2025-09-05T20:38:23.111755910Z"
traceSampled: false
}