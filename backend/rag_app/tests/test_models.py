from unittest.mock import patch, MagicMock
import sys

# huggingface_hubのモックを詳細に設定
huggingface_hub_mock = MagicMock()
huggingface_hub_mock.constants = MagicMock()
huggingface_hub_mock.constants.HF_HUB_DISABLE_TELEMETRY = False
sys.modules['huggingface_hub'] = huggingface_hub_mock
sys.modules['huggingface_hub.constants'] = huggingface_hub_mock.constants

# transformersモジュールを詳細にモック
transformers_mock = MagicMock()
transformers_utils_mock = MagicMock()
transformers_utils_versions_mock = MagicMock()
transformers_utils_versions_mock.require_version = MagicMock()
transformers_utils_versions_mock.require_version_core = MagicMock()
transformers_utils_mock.versions = transformers_utils_versions_mock
transformers_mock.utils = transformers_utils_mock
transformers_mock.dependency_versions_check = MagicMock()
transformers_mock.pipeline = MagicMock()
sys.modules['transformers'] = transformers_mock
sys.modules['transformers.utils'] = transformers_utils_mock
sys.modules['transformers.utils.versions'] = transformers_utils_versions_mock
sys.modules['transformers.dependency_versions_check'] = transformers_mock.dependency_versions_check

# その他の外部モジュールをモック
sys.modules['sentence_transformers'] = MagicMock()
sys.modules['opensearchpy'] = MagicMock()

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