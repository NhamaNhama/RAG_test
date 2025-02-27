from huggingface_hub import hf_hub_download

model_path = hf_hub_download(
    repo_id="facebook/mbart-large-50-many-to-many-mmt",
    filename="pytorch_model.bin",
    revision="main",
)
