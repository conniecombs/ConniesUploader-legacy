# modules/async_upload_manager.py
"""
Async Upload Manager - Performance-Optimized Concurrent Uploads

Uses asyncio and httpx.AsyncClient for efficient concurrent uploads.
Significantly better resource utilization than ThreadPoolExecutor.
"""

import asyncio
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
from . import api
from . import config
from .config_loader import get_config_loader
from .error_handler import handle_upload_error, handle_network_error
from .retry_utils import is_retryable_error
from .plugin_adapter import get_service_registry
from loguru import logger


# Load application configuration
_app_config = get_config_loader().config


class AsyncUploadManager:
    """
    Async upload manager using asyncio for concurrent uploads.

    Benefits over ThreadPoolExecutor:
    - Lower memory overhead (coroutines vs threads)
    - Better CPU utilization
    - Easier to control concurrency
    - More scalable for high concurrency
    """

    def __init__(self, progress_queue, result_queue, cancel_event):
        self.progress_queue = progress_queue
        self.result_queue = result_queue
        self.cancel_event = cancel_event
        self.service_registry = get_service_registry()

    def start_batch(self, pending_by_group, cfg, creds):
        """
        Start async upload batch in a separate thread.

        Uses asyncio.run() in a thread to avoid blocking the tkinter UI.
        """
        import threading

        def run_async_batch():
            """Wrapper to run async code in a thread."""
            try:
                asyncio.run(self._run_async_uploads(pending_by_group, cfg, creds))
            except Exception as e:
                logger.error(f"Async batch error: {e}")

        threading.Thread(target=run_async_batch, daemon=True).start()

    async def _run_async_uploads(self, pending_by_group, base_cfg, creds):
        """
        Main async upload orchestrator.

        Creates an AsyncClient and runs concurrent uploads with controlled concurrency.
        """
        # Determine concurrency based on service
        service_prefix = base_cfg['service'].split('.')[0]
        if service_prefix == 'turboimagehost':
            max_concurrent = base_cfg.get('turbo_threads', 2)
        else:
            max_concurrent = base_cfg.get(f"{service_prefix}_threads", 2)

        logger.info(f"Starting async uploads with max_concurrent={max_concurrent}")

        # Create async HTTP client
        async with api.create_async_client() as client:
            for group, files in pending_by_group.items():
                if self.cancel_event.is_set():
                    break

                # Prepare configuration for this group
                current_cfg = base_cfg.copy()
                current_pix_data = {}

                # --- Gallery Creation Logic (sync operations) ---
                await self._handle_gallery_creation(
                    base_cfg, group, current_cfg, current_pix_data, creds, client
                )

                # --- Concurrent File Uploads ---
                await self._upload_files_concurrently(
                    files, group, current_cfg, current_pix_data, creds, client, max_concurrent
                )

        logger.info("Async batch execution finished.")

    async def _handle_gallery_creation(self, base_cfg, group, current_cfg, current_pix_data, creds, client):
        """Handle gallery creation for different services."""
        service = base_cfg['service']

        if service == "pixhost.to":
            if base_cfg.get('auto_gallery'):
                clean_title = group.title.replace('[', '').replace(']', '').strip()
                logger.info(f"Creating Pixhost gallery: {clean_title}")

                # Gallery creation is sync for now (could be async later)
                new_data = await asyncio.to_thread(
                    api.create_pixhost_gallery, clean_title
                )

                if new_data:
                    current_pix_data.update(new_data)
                    self.progress_queue.put(('register_pix_gal', None, new_data))
                    group.gallery_id = new_data.get('gallery_hash', '')
                else:
                    logger.warning(f"Failed to create gallery '{clean_title}'")

            elif base_cfg.get('pix_gallery_hash'):
                current_pix_data['gallery_hash'] = base_cfg['pix_gallery_hash']
                group.gallery_id = base_cfg['pix_gallery_hash']

        elif service == "imx.to" and base_cfg.get('auto_gallery'):
            # IMX gallery creation (sync for now)
            gid = await asyncio.to_thread(
                api.create_imx_gallery,
                creds.get('imx_user'),
                creds.get('imx_pass'),
                group.title
            )
            if gid:
                current_cfg['gallery_id'] = gid
                group.gallery_id = gid

    async def _upload_files_concurrently(self, files, group, cfg, pix_data, creds, client, max_concurrent):
        """
        Upload files concurrently with semaphore-controlled concurrency.

        Uses asyncio.Semaphore to limit concurrent uploads.
        """
        semaphore = asyncio.Semaphore(max_concurrent)

        async def upload_with_semaphore(fp, is_first):
            """Wrapper to control concurrency."""
            async with semaphore:
                if self.cancel_event.is_set():
                    return
                await self._upload_task_async(fp, is_first, cfg, pix_data, creds, client)

        # Create tasks for all files
        tasks = [
            upload_with_semaphore(fp, fp == group.files[0])
            for fp in files
        ]

        # Run concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    async def _upload_task_async(self, fp, is_first, cfg, pix_data, creds, client):
        """
        Async upload task for a single file.

        Main upload logic with async HTTP and retry handling.
        """
        if self.cancel_event.is_set():
            return

        self.progress_queue.put(('status', fp, 'Uploading'))

        try:
            # Progress callback
            def progress_callback(monitor):
                if self.cancel_event.is_set():
                    raise Exception("Cancelled")
                if monitor.len > 0:
                    self.progress_queue.put(('prog', fp, (monitor.bytes_read / monitor.len)))

            # Instantiate uploader (sync operation)
            uploader = self._create_uploader(
                cfg['service'], fp, is_first, cfg, pix_data, progress_callback, client
            )

            if not uploader:
                raise Exception(f"Unsupported service: {cfg['service']}")

            # Perform async upload with retry
            img, thumb = await self._perform_async_upload(uploader, fp, cfg, client)

            # Success
            self.result_queue.put((fp, img, thumb))
            self.progress_queue.put(('status', fp, 'Done'))

        except Exception as e:
            self.progress_queue.put(('status', fp, 'Failed'))
            handle_upload_error(
                error=e,
                file_path=fp,
                service=cfg.get('service', 'unknown')
            )
        finally:
            if uploader:
                uploader.close()

    def _create_uploader(self, service, fp, is_first, cfg, pix_data, callback, client):
        """Create appropriate uploader instance based on service."""
        # Check if this is a plugin service
        if self.service_registry.is_plugin_service(service):
            logger.info(f"Using plugin service: {service}")
            return self._create_plugin_uploader(service, fp, cfg, callback)

        # Built-in services
        if service == "imx.to":
            th = "600" if (is_first and cfg['imx_cover']) else cfg['imx_thumb']
            return api.ImxUploader(
                cfg['api_key'], fp, callback, th,
                cfg.get('imx_format', 'Fixed Width'),
                cfg.get('gallery_id')
            )

        elif service == "pixhost.to":
            is_cov = (is_first and cfg['pix_cover'])
            return api.PixhostUploader(
                fp, callback, cfg['pix_content'], cfg['pix_thumb'],
                pix_data.get('gallery_hash'),
                pix_data.get('gallery_upload_hash'),
                is_cov
            )

        elif service == "turboimagehost":
            th = "600" if (is_first and cfg.get('turbo_cover')) else cfg['turbo_thumb']
            return api.TurboUploader(
                fp, callback, config.TURBO_HOME_URL,
                api.generate_turbo_upload_id(),
                cfg['turbo_content'], th, cfg['turbo_gal_id'],
                client=client
            )

        elif service == "vipr.im":
            th = "800x800" if (is_first and cfg.get('vipr_cover')) else cfg['vipr_thumb']
            return api.ViprUploader(
                fp, callback,
                cfg.get('vipr_meta', {}).get('upload_url', config.VIPR_HOME_URL),
                "", th, cfg['vipr_gal_id'],
                client=client
            )

        return None

    def _create_plugin_uploader(self, service_name, fp, cfg, callback):
        """Create a plugin uploader wrapped in an adapter."""
        # Get plugin credentials from config
        plugin_creds = cfg.get('plugin_credentials', {}).get(service_name, {})

        # Create plugin instance
        plugin = self.service_registry.get_plugin_instance(
            service_name,
            credentials=plugin_creds,
            config=cfg
        )

        if not plugin:
            raise Exception(f"Failed to create plugin instance for {service_name}")

        # Wrap plugin in adapter to match existing uploader interface
        return PluginUploaderAdapter(plugin, fp, callback)

    async def _perform_async_upload(self, uploader, fp, cfg, client):
        """
        Perform async HTTP upload with retry logic.

        Retries on network errors with exponential backoff.
        """
        url, data, headers = uploader.get_request_params()

        # Add Content-Length if not present
        if 'Content-Length' not in headers and hasattr(data, 'len'):
            headers['Content-Length'] = str(data.len)

        max_attempts = _app_config.network.retry_count
        base_delay = 2.0
        service = cfg['service']

        for attempt in range(1, max_attempts + 1):
            try:
                self.progress_queue.put(('status', fp, 'Uploading'))

                # Read data chunks (async generator)
                async def read_chunks():
                    chunk_size = _app_config.network.chunk_size
                    while True:
                        # Read in executor to avoid blocking
                        chunk = await asyncio.to_thread(data.read, chunk_size)
                        if not chunk:
                            break
                        yield chunk

                # Perform async upload
                response = await client.post(
                    url,
                    headers=headers,
                    content=read_chunks(),
                    timeout=_app_config.network.upload_timeout_seconds
                )

                # Parse response
                resp_data = response.text if service == 'vipr.im' else response.json()
                img, thumb = uploader.parse_response(resp_data)

                return img, thumb

            except Exception as e:
                if attempt < max_attempts and is_retryable_error(e):
                    delay = min(base_delay * (2 ** (attempt - 1)), 30.0)
                    logger.warning(f"Upload attempt {attempt} failed for {fp}, retrying in {delay}s: {e}")
                    await asyncio.sleep(delay)
                else:
                    # Last attempt or non-retryable error
                    if is_retryable_error(e):
                        handle_network_error(e, "Upload", service)
                    raise


class PluginUploaderAdapter:
    """
    Adapter to make plugin uploaders compatible with the existing uploader interface.

    Plugins use a different interface than built-in uploaders, so this adapter
    translates between the two.
    """

    def __init__(self, plugin, file_path, progress_callback):
        """
        Initialize adapter.

        Args:
            plugin: ImageHostPlugin instance
            file_path: Path to file to upload
            progress_callback: Progress callback function
        """
        self.plugin = plugin
        self.file_path = Path(file_path)
        self.progress_callback = progress_callback
        self._result = None

    def get_request_params(self):
        """
        Get upload request parameters.

        For plugins, we perform the upload directly in this method
        and store the result for later retrieval by parse_response().

        This is a workaround to adapt the plugin interface to the existing
        uploader interface which expects separate get_request_params() and
        parse_response() calls.

        Returns:
            Dummy values (upload is already done)
        """
        try:
            # Plugins handle upload internally, so we call upload here
            self._result = self.plugin.upload(self.file_path, self._progress_wrapper)

            # Return dummy values since upload is already done
            return ("https://dummy.com", b"", {})

        except Exception as e:
            logger.error(f"Plugin upload failed: {e}")
            raise

    def _progress_wrapper(self, bytes_sent, total_bytes):
        """Wrap plugin progress callback to match expected interface."""
        if self.progress_callback:
            # Create a mock monitor object with the expected attributes
            class MockMonitor:
                def __init__(self, bytes_read, length):
                    self.bytes_read = bytes_read
                    self.len = length

            monitor = MockMonitor(bytes_sent, total_bytes)
            self.progress_callback(monitor)

    def parse_response(self, response_data):
        """
        Parse upload response.

        Since the upload was already done in get_request_params(),
        we just return the stored result here.

        Args:
            response_data: Ignored (upload already done)

        Returns:
            Tuple of (image_url, thumb_url)
        """
        if self._result:
            return (self._result.image_url, self._result.thumb_url)

        raise Exception("Plugin upload failed: no result available")

    def close(self):
        """Cleanup plugin resources."""
        if self.plugin:
            try:
                self.plugin.cleanup()
            except Exception as e:
                logger.warning(f"Plugin cleanup error: {e}")
