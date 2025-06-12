from backend.services import llm_service

# THE ONLY WAY to do inference - automatic logging!
result = llm_service.inference_request(
    prompt="please respond with just the word 'hi' and nothing eles",
)

print(result['text'])  # Should print "hi"