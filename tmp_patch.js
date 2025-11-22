const fs = require('fs');
const path = 'backend/app/utils/diagram_wizard/nodes/clarification_nodes.py';
let content = fs.readFileSync(path, 'utf8');
const pattern = /logger\.info\(\s*\n\s*f\"\?\? AI gathered enough information \(score: \{clarity_score\}\) \"\s*\n\s*f\\\"- \{'auto-proceeding' if auto_proceed_on_ready else 'waiting for user confirmation'\}\",\s*\n\s*extra=\{'session_id': session_id\} if session_id else {}\s*\n\s*\)/s;
const replacement = `logger.info(
                f"?? AI gathered enough information (score: {clarity_score}) - "
                f"{'auto-proceeding' if auto_proceed_on_ready else 'waiting for user confirmation'}",
                extra={'session_id': session_id} if session_id else {}
            )`;
if (!pattern.test(content)) {
  console.error('pattern not found');
  process.exit(1);
}
content = content.replace(pattern, replacement);
fs.writeFileSync(path, content);
