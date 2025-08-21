from backend.workflow.workflow_gateway import request_workflow

success, workflow_id = request_workflow( workflow_type="enter_dungeon")

print(success)
print(workflow_id)