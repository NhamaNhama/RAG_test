from unittest.mock import patch, MagicMock
import sys

# huggingface_hubのモックを詳細に設定
huggingface_hub_mock = MagicMock()
huggingface_hub_mock.constants = MagicMock()
huggingface_hub_mock.constants.HF_HUB_DISABLE_TELEMETRY = False
sys.modules['huggingface_hub'] = huggingface_hub_mock
sys.modules['huggingface_hub.constants'] = huggingface_hub_mock.constants

# その他の外部モジュールをモック
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['opensearchpy'] = MagicMock()
sys.modules['transformers'] = MagicMock()

@patch("backend.rag_app.views.hf_hub_download")
def test_model_behavior(mock_hf_download):
    # モックの戻り値を設定
    mock_hf_download.return_value = "/path/to/mocked/model/file"
    
    # テスト対象の関数を呼び出す
    from backend.rag_app.views import load_model_offline
    
    model_path = load_model_offline(
        repo_id="some-repo",
        filename="some-file"
    )
    
    # モックが呼び出されたことを確認
    mock_hf_download.assert_called_once()
    assert model_path == "/path/to/mocked/model/file" 