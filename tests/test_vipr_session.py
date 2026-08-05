"""
Tests for Vipr session cookie wiring into sync/async HTTP clients.
"""

import asyncio
from unittest.mock import MagicMock, patch, PropertyMock

import httpx
import pytest

from modules import api
from modules.async_upload_manager import AsyncUploadManager
from modules.app_state import ServiceAuthState


class TestCookieHelpers:
    def test_cookies_to_dict_from_dict(self):
        assert api.cookies_to_dict({"xfss": "abc", "uid": "1"}) == {
            "xfss": "abc",
            "uid": "1",
        }

    def test_cookies_to_dict_empty(self):
        assert api.cookies_to_dict(None) == {}
        assert api.cookies_to_dict({}) == {}

    def test_cookies_to_dict_from_httpx_cookies(self):
        client = httpx.Client()
        client.cookies.set("xfss", "session_token")
        client.cookies.set("lang", "en")
        result = api.cookies_to_dict(client.cookies)
        client.close()
        assert result.get("xfss") == "session_token"
        assert result.get("lang") == "en"

    def test_apply_cookies_to_sync_client(self):
        client = httpx.Client()
        api.apply_cookies(client, {"xfss": "tok", "other": "v"})
        jar = api.cookies_to_dict(client.cookies)
        client.close()
        assert jar["xfss"] == "tok"
        assert jar["other"] == "v"

    def test_apply_cookies_to_async_client(self):
        client = httpx.AsyncClient()
        api.apply_cookies(client, {"xfss": "async_tok"})
        jar = api.cookies_to_dict(client.cookies)
        asyncio.run(client.aclose())
        assert jar["xfss"] == "async_tok"

    def test_apply_cookies_noop_on_empty(self):
        client = httpx.Client()
        api.apply_cookies(client, None)
        api.apply_cookies(client, {})
        assert api.cookies_to_dict(client.cookies) == {}
        client.close()

    def test_create_async_client_with_cookies(self):
        client = api.create_async_client(cookies={"xfss": "from_factory"})
        jar = api.cookies_to_dict(client.cookies)
        asyncio.run(client.aclose())
        assert jar["xfss"] == "from_factory"


class TestEnsureViprAuth:
    def test_missing_credentials(self):
        cookies, meta = api.ensure_vipr_auth("", "pass")
        assert cookies is None and meta is None

        cookies, meta = api.ensure_vipr_auth("user", "")
        assert cookies is None and meta is None

    def test_reuses_valid_existing_cookies(self):
        existing = {"xfss": "keep_me"}
        fake_meta = {
            "upload_url": "https://vipr.im/upload.cgi",
            "sess_id": "abc123",
            "galleries": [{"id": "1", "name": "Album"}],
        }

        with patch("modules.api.create_resilient_client") as mock_create:
            mock_client = MagicMock()
            mock_client.cookies = existing
            mock_create.return_value = mock_client

            with patch("modules.api.get_vipr_metadata", return_value=fake_meta):
                with patch("modules.api.vipr_login") as mock_login:
                    cookies, meta = api.ensure_vipr_auth(
                        "user",
                        "pass",
                        existing_cookies=existing,
                        force_refresh=False,
                    )

        assert cookies["xfss"] == "keep_me"
        assert meta["sess_id"] == "abc123"
        mock_login.assert_not_called()
        mock_client.close.assert_called()

    def test_fresh_login_when_reuse_fails(self):
        fake_meta = {
            "upload_url": "https://vipr.im/upload.cgi",
            "sess_id": "new_sess",
            "galleries": [],
        }
        login_client = MagicMock()
        login_client.cookies = {"xfss": "new_token"}

        with patch("modules.api.create_resilient_client") as mock_create:
            reuse_client = MagicMock()
            # First client for reuse attempt, second for fresh login
            mock_create.side_effect = [reuse_client, login_client]

            with patch("modules.api.get_vipr_metadata", side_effect=[None, fake_meta]):
                with patch("modules.api.vipr_login", return_value=login_client) as mock_login:
                    cookies, meta = api.ensure_vipr_auth(
                        "user",
                        "pass",
                        existing_cookies={"xfss": "stale"},
                        force_refresh=False,
                    )

        assert cookies["xfss"] == "new_token"
        assert meta["sess_id"] == "new_sess"
        mock_login.assert_called_once()


class TestViprUploaderClientType:
    def test_does_not_use_async_client_for_sync_parse(self):
        async_client = httpx.AsyncClient()
        try:
            uploader = api.ViprUploader(
                "file.jpg",
                None,
                "https://vipr.im/upload.cgi",
                "sess",
                "170x170",
                client=async_client,
                cookies={"xfss": "tok"},
            )
            # Must own a sync Client, not the AsyncClient
            assert isinstance(uploader.client, httpx.Client)
            assert not isinstance(uploader.client, httpx.AsyncClient)
            assert uploader._owns_client is True
            jar = api.cookies_to_dict(uploader.client.cookies)
            assert jar.get("xfss") == "tok"
            uploader.close()
        finally:
            asyncio.run(async_client.aclose())

    def test_shared_sync_client_not_owned(self):
        sync = httpx.Client()
        api.apply_cookies(sync, {"xfss": "shared"})
        uploader = api.ViprUploader(
            "file.jpg",
            None,
            "https://vipr.im/upload.cgi",
            "sess",
            "170x170",
            client=sync,
        )
        assert uploader.client is sync
        assert uploader._owns_client is False
        uploader.close()  # must not close shared client
        # Shared client still usable
        assert api.cookies_to_dict(sync.cookies).get("xfss") == "shared"
        sync.close()


class TestAsyncManagerAppliesViprCookies:
    def test_run_async_creates_clients_with_cookies(self):
        import queue
        from unittest.mock import Mock

        progress = queue.Queue()
        result = queue.Queue()
        cancel = Mock()
        cancel.is_set.return_value = True  # exit loop immediately after client setup

        manager = AsyncUploadManager(progress, result, cancel)
        manager.service_registry = MagicMock()
        manager.service_registry.is_plugin_service.return_value = False

        cfg = {
            "service": "vipr.im",
            "vipr_cookies": {"xfss": "batch_cookie"},
            "vipr_meta": {"upload_url": "https://vipr.im/u", "sess_id": "s"},
            "vipr_threads": 1,
        }

        created_async = []
        created_sync = []

        real_async = api.create_async_client
        real_sync = api.create_resilient_client

        def track_async(*args, **kwargs):
            c = real_async(*args, **kwargs)
            created_async.append((c, api.cookies_to_dict(c.cookies)))
            return c

        def track_sync(*args, **kwargs):
            c = real_sync(*args, **kwargs)
            created_sync.append(c)
            return c

        with patch("modules.async_upload_manager.api.create_async_client", side_effect=track_async):
            with patch("modules.async_upload_manager.api.create_resilient_client", side_effect=track_sync):
                with patch("modules.async_upload_manager.api.apply_cookies", wraps=api.apply_cookies) as apply_spy:
                    asyncio.run(manager._run_async_uploads({}, cfg, {}))

        assert len(created_async) == 1
        assert created_async[0][1].get("xfss") == "batch_cookie"
        # Sync client was created and cookies applied
        assert apply_spy.called
        assert manager._vipr_sync_client is None  # cleaned up in finally


class TestAppStateViprAuth:
    def test_set_vipr_auth_updates_fields(self):
        auth = ServiceAuthState()
        auth.set_vipr_auth(
            {"xfss": "x"},
            {"sess_id": "1", "upload_url": "u"},
            galleries_map={"Album": "9"},
        )
        assert auth.vipr_cookies["xfss"] == "x"
        assert auth.vipr_meta["sess_id"] == "1"
        assert auth.vipr_galleries_map["Album"] == "9"

    def test_clear_vipr_clears_cookies(self):
        auth = ServiceAuthState()
        auth.set_vipr_auth({"xfss": "x"}, {"sess_id": "1"}, galleries_map={"A": "1"})
        auth.clear_vipr()
        assert auth.vipr_cookies is None
        assert auth.vipr_meta is None
        assert auth.vipr_galleries_map == {}
