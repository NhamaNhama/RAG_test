from huggingface_hub import hf_hub_download

def download_model(model_id: str, filename: str) -> str:
    return hf_hub_download(repo_id=model_id, filename=filename)

model_path = hf_hub_download(repo_id="...", filename="...")
... 