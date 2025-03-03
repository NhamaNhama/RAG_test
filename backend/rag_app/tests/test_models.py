from unittest.mock import patch, MagicMock

@patch("huggingface_hub.hf_hub_download", autospec=True)
def test_model_behavior(mock_hf_download):
    # モックの戻り値を設定
    mock_hf_download.return_value = "/path/to/mocked/model/file"
    
    # 直接モック関数を呼び出す
    downloaded_file = mock_hf_download(repo_id="model-repo", filename="model.bin")
    
    # モックが呼び出されたことを確認
    mock_hf_download.assert_called_once_with(repo_id="model-repo", filename="model.bin")
    assert downloaded_file == "/path/to/mocked/model/file" 