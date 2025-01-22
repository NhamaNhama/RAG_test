from huggingface_hub import hf_hub_download

def test_model_something():
    model_path = hf_hub_download(repo_id="...", filename="...")
    ... 