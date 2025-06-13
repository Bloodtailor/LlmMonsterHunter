from backend.services import llm_service

# THE ONLY WAY to do inference - automatic logging!
result = llm_service.inference_request(
    prompt="Time to get kicking",
)

print(result['text'])  # Should print "hi"