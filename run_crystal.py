import sys
import os
import time
import socket
import threading
import urllib.request
import subprocess
import argparse
import traceback

# Ensure current working directory / project root is on sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.config import NodeConfig
from src.node import create_app
import uvicorn


def _check_port_active(host: str, port: int) -> bool:
    """Check if a TCP port is currently accepting connections."""
    try:
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.settimeout(0.5)
            check_host = "127.0.0.1" if host in ("0.0.0.0", "", "::") else host
            return s.connect_ex((check_host, port)) == 0
    except Exception:
        return False


def _wait_for_server(health_url: str, timeout: float = 15.0) -> bool:
    """Poll health endpoint until HTTP 200 OK or timeout."""
    start_time = time.time()
    while time.time() - start_time < timeout:
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=1.0) as resp:
                if resp.status == 200:
                    return True
        except Exception:
            pass
        time.sleep(0.2)
    return False


def _launch_fallback_browser(app_url: str) -> None:
    """Fallback: open via Edge App mode or Windows Shell."""
    edge_paths = [
        r"C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe",
        r"C:\Program Files\Microsoft\Edge\Application\msedge.exe",
    ]
    for ep in edge_paths:
        if os.path.exists(ep):
            try:
                subprocess.Popen([ep, f"--app={app_url}"])
                return
            except Exception:
                pass
    try:
        subprocess.Popen(f'start "" "{app_url}"', shell=True)
    except Exception:
        pass


def launch():
    parser = argparse.ArgumentParser(description="Start Crystal Edge-AI Node")
    parser.add_argument("--config", type=str, default=None, help="Path to JSON configuration file")
    parser.add_argument("--host", type=str, default=None, help="Override listening host")
    parser.add_argument("--port", type=int, default=None, help="Override listening port")
    parser.add_argument("--headless", "--no-window", action="store_true", help="Run server without desktop window")
    
    args, _ = parser.parse_known_args()

    # Load configuration to determine listening host and port
    try:
        config = NodeConfig.load(config_path=args.config)
        if args.host:
            config.host = args.host
        if args.port:
            config.port = args.port
    except Exception as e:
        print(f"Warning: Failed to load config ({e}), using default NodeConfig.")
        config = NodeConfig()
        if args.host:
            config.host = args.host
        if args.port:
            config.port = args.port

    bind_host = config.host
    browser_host = "127.0.0.1" if bind_host in ("0.0.0.0", "", "::") else bind_host
    target_port = config.port
    app_url = f"http://{browser_host}:{target_port}/"
    health_url = f"http://{browser_host}:{target_port}/api/health"
    window_title = f"Crystal — {config.node_name} ({config.node_id})"

    print("=" * 60)
    print(f"  CRYSTAL EDGE AI — {config.node_name} ({config.node_id})")
    print(f"  Endpoint: {app_url}")
    print(f"  Storage:  {os.path.abspath(config.data_directory)}")
    print("=" * 60)

    # Check if a Crystal node is already running on this port
    if _check_port_active(bind_host, target_port):
        try:
            req = urllib.request.Request(health_url)
            with urllib.request.urlopen(req, timeout=1.5) as resp:
                if resp.status == 200:
                    print(f"\n[INFO] Crystal node is already running at {app_url}.")
                    print(f"[INFO] Opening desktop interface...")
                    if not args.headless:
                        try:
                            import webview
                            webview.create_window(window_title, app_url, width=1280, height=850, min_size=(960, 640))
                            webview.start()
                            return
                        except Exception:
                            _launch_fallback_browser(app_url)
                            return
                    return
        except Exception:
            pass

    # Initialize FastAPI application
    app = create_app(config)

    # If headless mode requested, run directly on main thread
    if args.headless:
        print(f"Starting Crystal Node in headless mode on http://{bind_host}:{target_port}")
        uvicorn.run(app, host=bind_host, port=target_port, log_level="info")
        return

    # Start Uvicorn in background daemon thread
    uvi_config = uvicorn.Config(
        app,
        host=bind_host,
        port=target_port,
        log_level="warning",
        access_log=False,
    )
    server = uvicorn.Server(uvi_config)
    server_thread = threading.Thread(target=server.run, daemon=True)
    server_thread.start()

    # Wait for server readiness
    print(f"Starting Crystal Node on {app_url}...")
    ready = _wait_for_server(health_url, timeout=15.0)
    if not ready:
        print("Warning: server health check timed out, attempting to display interface anyway.")
    else:
        print("Crystal server is ready. Launching desktop window...")

    # Launch desktop application window via pywebview
    webview_active = False
    try:
        import webview
        window = webview.create_window(
            title=window_title,
            url=app_url,
            width=1280,
            height=850,
            min_size=(960, 640),
            background_color="#FAF9F6",
        )
        webview_active = True
        webview.start(debug=False)
    except Exception as e:
        print(f"Native desktop window unavailable ({e}). Falling back to browser window...")
        _launch_fallback_browser(app_url)
        # Keep server thread alive if webview failed
        try:
            while not server.should_exit:
                time.sleep(1.0)
        except KeyboardInterrupt:
            pass

    # Clean shutdown when desktop window closes
    print("\nDesktop application closed. Shutting down Crystal node...")
    server.should_exit = True
    server_thread.join(timeout=3.0)
    print("Crystal node stopped cleanly.")


if __name__ == "__main__":
    try:
        launch()
    except Exception as e:
        print("\n" + "!" * 60)
        print(f"CRITICAL ERROR STARTING CRYSTAL: {e}")
        print("!" * 60)
        traceback.print_exc()
        try:
            input("\nPress Enter to exit...")
        except Exception:
            pass
        sys.exit(1)
