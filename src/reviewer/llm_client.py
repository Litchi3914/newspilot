class LLMClient:
    def generate_json(self, prompt: str) -> dict:
        return {'mock': True, 'prompt_len': len(prompt)}
    def generate_text(self, prompt: str) -> str:
        return prompt
