from huggingface_hub import hf_hub_download

def download_model(model_id: str, filename: str) -> str:
    return hf_hub_download(
        repo_id=model_id,
        filename=filename,
        revision="main",
    )

model_path = hf_hub_download(
    repo_id="facebook/mbart-large-50-many-to-many-mmt",
    filename="pytorch_model.bin",
    revision="main",
)

def get_model_path():
    model_path = hf_hub_download(
        repo_id="facebook/mbart-large-50-many-to-many-mmt",
        filename="pytorch_model.bin",
        revision="main",
    )
    return model_path

... 