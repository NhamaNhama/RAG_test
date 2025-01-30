from huggingface_hub import hf_hub_download

def download_model(model_id: str, filename: str) -> str:
    return hf_hub_download(repo_id=model_id, filename=filename)

model_path = hf_hub_download(repo_id="facebook/mbart-large-50-many-to-many-mmt", filename="pytorch_model.bin")

def get_model_path():
    model_path = hf_hub_download(repo_id="facebook/mbart-large-50-many-to-many-mmt", filename="pytorch_model.bin")
    return model_path

... 