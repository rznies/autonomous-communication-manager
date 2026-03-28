from emailmanagement.settings import AppSettings


def test_settings_default_to_local_dev_values(monkeypatch):
    monkeypatch.delenv("ACM_ENV", raising=False)
    monkeypatch.delenv("ACM_DB_PATH", raising=False)
    monkeypatch.delenv("ACM_CORS_ORIGINS", raising=False)
    monkeypatch.delenv("ACM_MUTATION_API_KEY", raising=False)

    settings = AppSettings.from_env()

    assert settings.environment == "development"
    assert settings.docs_enabled is True
    assert settings.auth_mode == "none"
    assert settings.cors_origins == ("http://localhost:5173",)


def test_settings_enable_prod_auth_and_disable_docs(monkeypatch, tmp_path):
    monkeypatch.setenv("ACM_ENV", "production")
    monkeypatch.setenv("ACM_DB_PATH", str(tmp_path / "prod.db"))
    monkeypatch.setenv(
        "ACM_CORS_ORIGINS", "https://app.example.com,https://ops.example.com"
    )
    monkeypatch.setenv("ACM_MUTATION_API_KEY", "prod-secret")
    monkeypatch.setenv("ACM_ENABLE_DOCS", "false")
    monkeypatch.setenv("ACM_HAS_WRITE_SCOPE", "true")

    settings = AppSettings.from_env()

    assert settings.environment == "production"
    assert settings.db_path == str(tmp_path / "prod.db")
    assert settings.cors_origins == (
        "https://app.example.com",
        "https://ops.example.com",
    )
    assert settings.requires_api_key is True
    assert settings.auth_mode == "x-acm-api-key"
    assert settings.docs_enabled is False
    assert settings.has_write_scope is True
