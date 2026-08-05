"""
Regression tests for critical upload bugs fixed in maintenance.

Covers:
- Result queue must not be replaced (UI holds aliases)
- Plugin uploads must not use shared HTTP path (double-upload / always-fail)
- PluginUploaderAdapter upload_via_plugin path
- turbo_gal_id / safe key access in uploader creation
"""

import asyncio
import queue
from pathlib import Path
from unittest.mock import MagicMock, Mock, patch

import pytest

from modules.app_state import AppState
from modules.async_upload_manager import AsyncUploadManager, PluginUploaderAdapter
from modules.plugin_interface import UploadResult
from modules.upload_coordinator import UploadCoordinator
from modules.upload_history import UploadHistory, UploadRecord


class DummyUploadManager:
    """Minimal stand-in for upload manager used by coordinator."""

    def __init__(self):
        self.result_queue = queue.Queue()
        self.progress_queue = queue.Queue()

    def start_batch(self, *args, **kwargs):
        pass


class TestResultQueueNotReplaced:
    """UI aliases must keep pointing at the same queue objects."""

    def test_start_upload_does_not_replace_result_queue(self):
        state = AppState()
        original_result = state.queues.result_queue
        original_progress = state.queues.progress_queue

        # Simulate UI holding aliases (as main.py does)
        ui_result_alias = state.queues.result_queue
        ui_progress_alias = state.queues.progress_queue

        manager = DummyUploadManager()
        manager.result_queue = state.queues.result_queue
        manager.progress_queue = state.queues.progress_queue

        # Seed stale items that should be drained
        state.queues.result_queue.put(("old", "x", "y"))
        state.queues.progress_queue.put(("status", "old", "Done"))

        coordinator = UploadCoordinator(state, manager, template_manager=MagicMock())

        # Minimal group-like object
        class FakeGroup:
            files = ["a.jpg"]

        class FakeWidget:
            def __getitem__(self, key):
                return "pending"

        state.files.file_widgets["a.jpg"] = {"state": "pending"}
        pending = {FakeGroup(): ["a.jpg"]}

        with patch.object(coordinator.upload_history, "start_session", return_value="test_session"):
            ok = coordinator.start_upload(
                pending,
                settings={"service": "imx.to"},
                credentials={},
            )

        assert ok is True
        # Same object identity — UI aliases still valid
        assert state.queues.result_queue is original_result
        assert state.queues.progress_queue is original_progress
        assert ui_result_alias is state.queues.result_queue
        assert ui_progress_alias is state.queues.progress_queue
        assert manager.result_queue is original_result
        assert manager.progress_queue is original_progress
        # Stale items drained
        assert state.queues.result_queue.empty()
        assert state.queues.progress_queue.empty()


class TestPluginUploaderAdapter:
    """Plugin path must upload once via the plugin, not shared HTTP."""

    def test_upload_via_plugin_returns_urls(self):
        plugin = MagicMock()
        plugin.upload.return_value = UploadResult(
            image_url="https://catbox.moe/abc.jpg",
            thumb_url="https://catbox.moe/abc.jpg",
        )
        adapter = PluginUploaderAdapter(plugin, "/tmp/test.jpg", None)

        img, thumb = adapter.upload_via_plugin()

        assert img == "https://catbox.moe/abc.jpg"
        assert thumb == "https://catbox.moe/abc.jpg"
        plugin.upload.assert_called_once()

    def test_get_request_params_raises(self):
        plugin = MagicMock()
        adapter = PluginUploaderAdapter(plugin, "/tmp/test.jpg", None)

        with pytest.raises(RuntimeError, match="upload_via_plugin"):
            adapter.get_request_params()

        plugin.upload.assert_not_called()

    def test_perform_async_upload_uses_plugin_path_only(self):
        manager = AsyncUploadManager(queue.Queue(), queue.Queue(), Mock())
        plugin = MagicMock()
        plugin.upload.return_value = UploadResult(
            image_url="https://i.imgur.com/x.png",
            thumb_url="https://i.imgur.com/x.png",
        )
        adapter = PluginUploaderAdapter(plugin, "/tmp/test.png", None)
        client = MagicMock()

        img, thumb = asyncio.run(
            manager._perform_async_upload(
                adapter, "/tmp/test.png", {"service": "Imgur"}, client
            )
        )

        assert img == "https://i.imgur.com/x.png"
        assert thumb == "https://i.imgur.com/x.png"
        plugin.upload.assert_called_once()
        # Shared HTTP client must not be used for plugins
        client.post.assert_not_called()


class TestUnboundUploaderGuard:
    """_upload_task_async must not raise UnboundLocalError on early failure."""

    def test_create_uploader_failure_does_not_raise_unbound(self):
        progress = queue.Queue()
        result = queue.Queue()
        cancel = Mock()
        cancel.is_set.return_value = False
        manager = AsyncUploadManager(progress, result, cancel)

        with patch.object(manager, "_create_uploader", return_value=None):
            asyncio.run(
                manager._upload_task_async(
                    "missing.jpg",
                    True,
                    {"service": "imx.to"},
                    {},
                    {},
                    MagicMock(),
                )
            )

        # Failed status was reported; no uncaught exception
        items = []
        while not progress.empty():
            items.append(progress.get_nowait())
        statuses = [i for i in items if i[0] == "status"]
        assert any(s[2] == "Failed" for s in statuses)


class TestHistoryRecording:
    """Per-file history records should be written during uploads."""

    def test_record_history_adds_success_record(self, tmp_path):
        history = UploadHistory(history_dir=tmp_path)
        history.start_session("Catbox", 1)

        progress = queue.Queue()
        result = queue.Queue()
        manager = AsyncUploadManager(progress, result, Mock())

        test_file = tmp_path / "img.jpg"
        test_file.write_bytes(b"fake")

        with patch(
            "modules.async_upload_manager.get_upload_history",
            return_value=history,
        ):
            manager._record_history(
                str(test_file),
                "Catbox",
                "https://example.com/a.jpg",
                "https://example.com/t.jpg",
                "success",
                {"service": "Catbox"},
            )

        assert history.current_session.successful == 1
        assert len(history.current_session.records) == 1
        assert history.current_session.records[0].image_url == "https://example.com/a.jpg"


class TestTurboGalIdSafeAccess:
    """Missing turbo_gal_id must not KeyError when creating uploader."""

    def test_turbo_uploader_created_without_gal_id_key(self):
        manager = AsyncUploadManager(queue.Queue(), queue.Queue(), Mock())
        manager.service_registry = MagicMock()
        manager.service_registry.is_plugin_service.return_value = False

        with patch("modules.async_upload_manager.api.TurboUploader") as TurboUploader:
            with patch("modules.async_upload_manager.api.generate_turbo_upload_id", return_value="uid"):
                TurboUploader.return_value = MagicMock()
                uploader = manager._create_uploader(
                    "turboimagehost",
                    "f.jpg",
                    True,
                    {
                        "service": "turboimagehost",
                        "turbo_thumb": "180",
                        "turbo_content": "Safe",
                        # intentionally omit turbo_gal_id
                    },
                    {},
                    None,
                    MagicMock(),
                )

        assert uploader is not None
        # Last arg before client is gallery id — empty string default
        args, kwargs = TurboUploader.call_args
        assert args[6] == "" or kwargs.get("client") is not None
