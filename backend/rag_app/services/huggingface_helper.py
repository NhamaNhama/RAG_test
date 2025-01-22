from huggingface_hub import hf_hub_download

def download_model(model_id: str, filename: str) -> str:
    return hf_hub_download(repo_id=model_id, filename=filename)

model_path = hf_hub_download(repo_id="...", filename="...")

def get_model_path():
    model_path = hf_hub_download(repo_id="my_org/my_repo", filename="my_model.bin")
    return model_path

... 