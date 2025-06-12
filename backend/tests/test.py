from backend.services import llm_service

# THE ONLY WAY to do inference - automatic logging!
result = llm_service.inference_request(
    prompt="'hi'",
)

print(result['text'])  # Should print "hi"