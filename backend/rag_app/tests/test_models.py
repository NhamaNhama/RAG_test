from huggingface_hub import hf_hub_download

def test_model_behavior():
    downloaded_file = hf_hub_download(repo_id="model-repo", filename="model.bin")
    ... 