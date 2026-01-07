from tenacity import retry, stop_after_attempt, wait_fixed

retry_llm = retry(
    stop=stop_after_attempt(2),
    wait=wait_fixed(1)
)
