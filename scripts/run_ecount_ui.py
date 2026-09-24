#!/usr/bin/env python3
"""
Launcher chạy giao diện nguyên bản ECOUNT ERP (không qua redesign) dưới dạng Native Desktop App.
Mã nguồn HTML, CSS và DOM được giữ nguyên 100% từ hệ thống gốc.
"""
import http.server
import socketserver
import subprocess
import threading
from pathlib import Path

# Thư mục chứa giao diện nguyên bản ECOUNT ERP
UI_DIR = Path(__file__).resolve().parent.parent / "docs" / "reference_ui"
PORT = 28080


class QuietHTTPHandler(http.server.SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(UI_DIR), **kwargs)

    def log_message(self, fmt, *args):
        # Tắt bớt log HTTP để terminal gọn gàng
        pass


def start_server() -> socketserver.TCPServer:
    # Cho phép tái sử dụng port ngay khi khởi động lại
    socketserver.TCPServer.allow_reuse_address = True
    server = socketserver.TCPServer(("127.0.0.1", PORT), QuietHTTPHandler)
    server_thread = threading.Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    return server


def launch_native_window() -> None:
    target_url = f"http://127.0.0.1:{PORT}/index.html"
    print("=" * 70)
    print("  WAREHOUSE ATLAS — ECOUNT ERP NATIVE DESKTOP INTERFACE")
    print("  Giữ nguyên 100% mã nguồn gốc, không tự redesign.")
    print(f"  URL Local Server: {target_url}")
    print("=" * 70)

    # Thử khởi chạy bằng PyWebView (sử dụng engine WebKit2 của Linux)
    try:
        import webview

        print("-> Đang mở cửa sổ Native Desktop qua WebKit2 / PyWebView...")
        webview.create_window(
            title="ECOUNT ERP — Giao Diện Quản Trị Kho Tham Chiếu Gốc",
            url=target_url,
            width=1440,
            height=900,
            resizable=True,
            confirm_close=False,
        )
        webview.start(gui="gtk")
        return
    except Exception as e:
        print(f"-> PyWebView gặp thông báo: {e}. Đang chuyển sang Standalone App Mode (Chrome)...")

    # Fallback mượt mà: Mở qua Chrome/Chromium ở chế độ App Window (không thanh URL, giao diện desktop độc lập)
    try:
        subprocess.run(
            [
                "google-chrome",
                f"--app={target_url}",
                "--window-size=1440,900",
                "--user-data-dir=/tmp/ecount_app_profile",
            ],
            check=True,
        )
    except Exception as e_chrome:
        print(f"Lỗi khởi chạy: {e_chrome}")
        print(f"Bạn có thể mở trực tiếp tại trình duyệt qua đường dẫn: {target_url}")


def main() -> None:
    server = start_server()
    try:
        launch_native_window()
    finally:
        server.shutdown()


if __name__ == "__main__":
    main()
