# -*- coding: utf-8 -*-

from __future__ import annotations

import os
import sys
import time
import datetime
import threading
import msvcrt
from zk import ZK
import requests # เพิ่ม library สำหรับส่ง HTTP request

import colorama as cl

from typing import TYPE_CHECKING, Union

if TYPE_CHECKING:
    from zk.attendance import Attendance

__devices__ = [
    {'ip': '192.168.1.202', 'port': 4370, 'name': 'Device 1' , 'sensor' : "1"},
    # เพิ่มเครื่องอื่น ๆ ที่นี่ตามต้องการ
]

# --- ตั้งค่า LINE Notify ---
LINE_NOTIFY_TOKEN = "LINE_NOTIFY_TOKEN" # <-- สำคัญ: ใส่ Token ของคุณที่นี่
LINE_NOTIFY_URL = "https://api.line.me/v2/bot/message/push"
# Branch 2 TARGET_USER_ID = "Ce33014cfc04b03526108e03c27fb7cad"
TARGET_USER_ID = "TARGET_USER_ID"
# --------------------------

# ไม่ใช้ __user_cached__ แล้ว เพราะไม่มีการ query จาก database
# __user_cached__: dict[int, int] = {}

class DeviceInterface:

    def __init__(self, ip: str, port: int, name: str, sensor: str) -> None:
        self.ip = ip
        self.port = port
        self.name = name
        self.sensor = sensor
        self.zk: ZK | None = None

    @property
    def is_connected(self) -> bool:
        if self.is_online and self.zk is not None:
            try:
                self.zk.get_serialnumber()
                return True
            except Exception:
                if self.reconnect():
                    try:
                        self.zk.get_serialnumber()
                        return True
                    except Exception:
                        return False
                else:
                    return False
        else:
            return False

    @property
    def is_online(self) -> bool:
        temp_zk = self.zk if self.zk else ZK(self.ip, port=self.port, timeout=5)
        try:
            return temp_zk.ping()
        except Exception:
            return False

    def reconnect(self) -> bool:
        terminal_logging(f"{clf.YELLOW}Attempting to reconnect {self.name}...{clf.RESET}")
        try:
            if self.zk:
                try:
                    self.zk.disconnect()
                except Exception:
                    pass
            self.zk = ZK(self.ip, port=self.port, timeout=10)
            self.zk.connect()
            self.zk.enable_device()
            terminal_logging(f"{self.name} - {clf.GREEN}Reconnected successfully{clf.RESET}")
            return True
        except Exception as e:
            terminal_logging(f"{self.name} - {clf.RED}Reconnect failed{clf.RESET}: {e}")
            self.zk = None
            return False


APP_NAME: str = "PNW realtime-zk (No DB - LINE Notify)"

devices: list[DeviceInterface] = []
for d in __devices__:
    d_obj = DeviceInterface(**d)
    devices.append(d_obj)

_app_first_run: bool = True
_do_logging: bool = True


cl.init(True)
clf = cl.Fore

CWD = os.path.dirname(os.path.realpath(__file__))
ROOT_DIR = os.path.dirname(CWD)
sys.path.append(ROOT_DIR)

os.system(f"title {APP_NAME}")

LOG_AT = "log_attendance/"

def strnow() -> str:
    return datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def terminal_logging(msg: str, *, t: str = "", **kwargs) -> None:
    if not _do_logging: return
    if t == "":
        t = f"{clf.LIGHTBLACK_EX}[{strnow()}]{clf.RESET}"
    print(t, msg, **kwargs)


def send_line_notify(message: str) -> None:
    """ส่งข้อความไปยัง LINE Notify"""
    if not LINE_NOTIFY_TOKEN or LINE_NOTIFY_TOKEN == "YOUR_LINE_NOTIFY_TOKEN":
        terminal_logging(f"{clf.YELLOW}LINE Notify token is not set. Skipping notification.{clf.RESET}")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {LINE_NOTIFY_TOKEN}"
    }
    payload = {
        "to": TARGET_USER_ID,
        "messages": [
            {
                "type": "text",
                "text": message
            }
        ]
    }

    try:
        response = requests.post(LINE_NOTIFY_URL, headers=headers, json=payload, timeout=10)
        response.raise_for_status()
        # terminal_logging(f"{clf.GREEN}Sent notification to LINE successfully.{clf.RESET}")
    except requests.exceptions.RequestException as e:
        terminal_logging(f"{clf.RED}Failed to send LINE notification{clf.RESET}: {e}")
    except Exception as e:
        terminal_logging(f"{clf.RED}An unexpected error occurred during LINE notification{clf.RESET}: {e}")


def capture_attendance(device: DeviceInterface) -> None:
    first_run = True
    connection = None
    user_cache = {}
    while capture:
        try:
            if device.zk is None or not device.is_connected:
                terminal_logging(f"{device.name} - {clf.YELLOW}Attempting to connect...{clf.RESET}")
                zk = ZK(device.ip, port=device.port, timeout=10) # เพิ่ม timeout
                connection = zk.connect()
                connection.enable_device()
                device.zk = zk
                users = connection.get_users()

                try:
                    users = connection.get_users()
                    for user in users:
                        user_cache[user.user_id] = user.name if hasattr(user, 'name') else f"User {user.user_id}"
                    terminal_logging(f"{device.name} - {clf.GREEN}Loaded {len(user_cache)} user records{clf.RESET}")
                except Exception as e:
                    terminal_logging(f"{device.name} - {clf.YELLOW}Warning: Could not load user data: {e}{clf.RESET}")
                
                if first_run and _app_first_run:
                    terminal_logging(f"{device.name} - {clf.GREEN}Ready{clf.RESET}")
                    first_run = False
                else:
                    if device.is_connected:
                        terminal_logging(f"{device.name} - {clf.GREEN}Reconnected{clf.RESET}")
                    else:
                        terminal_logging(f"{device.name} - {clf.RED}Connection attempt finished, but device still not connected.{clf.RESET}")
                        device.zk = None
                        time.sleep(15)
                        continue

            for attendance in device.zk.live_capture():
                if attendance is not None:
                    user_id = attendance.user_id
                    user_name = user_cache.get(user_id, f"User {user_id}")
                    timestamp = attendance.timestamp
                    station = "ํYourCompany HQ"
                    data_line = f"{device.name} - User: {user_id}, Time: {timestamp}, Sensor: {device.sensor}\n"

                    os.makedirs(LOG_AT, exist_ok=True)
                    now = datetime.datetime.now()
                    file_name = os.path.join(LOG_AT, f"{device.name}_{now.strftime('%Y-%m-%d')}.txt")

                    try:
                        with open(file_name, 'a', encoding='utf-8') as file: # เพิ่ม encoding='utf-8'
                            file.write(data_line)
                    except IOError as e:
                        terminal_logging(f"{clf.RED} An error occurred while writing to the log file{clf.RESET}: {e}")
                    except Exception as e:
                        terminal_logging(f"{clf.RED} An unexpected error occurred during log writing{clf.RESET}: {e}")

                    log_message = f"{clf.CYAN}Captured {clf.RESET}{str(user_id).ljust(5)} - {device.name} {clf.LIGHTBLACK_EX}sid: {device.sensor}"
                    terminal_logging(log_message, t=f"{clf.LIGHTBLACK_EX}[{timestamp}]{clf.RESET}")

                    line_message = f"📢 แจ้งเตือนการสแกนนิ้ว 📢\n👤 {user_name}\n🆔 รหัสพนักงาน: {user_id}\n⏰ เวลา: {datetime.datetime.now().strftime('%H:%M:%S')}\n📆 วันที่: {datetime.datetime.now().strftime('%d/%m/%Y')}\n📍 สถานที่: {station}"

                    send_line_notify(line_message)

                if stop_event.is_set() or not capture:
                    terminal_logging(f"{device.name} - Stopping capture...")
                    break

            if stop_event.is_set() or not capture:
                 break

            if capture:
                terminal_logging(f"{device.name} - {clf.RED}Lost connection (live_capture ended).{clf.RESET}")
                time.sleep(5)


        except Exception as e:
            terminal_logging(f"{device.name} - {clf.RED}An error occurred in capture loop{clf.RESET}: {e}")
            if device.zk:
                try:
                    device.zk.disconnect()
                except:
                    pass
            device.zk = None
            time.sleep(15)

        finally:
            if stop_event.is_set() or not capture:
                 if device.zk:
                     terminal_logging(f"{device.name} - Disconnecting ZK...")
                     try:
                         device.zk.disconnect()
                         terminal_logging(f"{device.name} - Disconnecting ZK... {clf.CYAN}done{clf.RESET}")
                     except Exception as disconnect_err:
                         terminal_logging(f"{device.name} - Disconnecting ZK... {clf.YELLOW}error during disconnect: {disconnect_err}{clf.RESET}")
                     device.zk = None
                 else:
                      terminal_logging(f"{device.name} - ZK already disconnected or not connected.")
                 break

    terminal_logging(f"{device.name} - {clf.MAGENTA}Capture thread terminated.{clf.RESET}")


def monitor_devices_status(devices: list[DeviceInterface]):
    while capture:
        if show_status:
            print()
            print(f"{clf.LIGHTBLACK_EX}Devices status at {strnow()}{clf.RESET}")
            all_connected = True
            for device in devices:
                is_conn = device.is_connected
                status = f"{clf.GREEN}online" if is_conn else f"{clf.RED}offline"
                print(str(f"{device.name}:").ljust(20), status) # เพิ่ม ljust
                if not is_conn:
                    all_connected = False
            print("-" * 30)
            if not all_connected:
                 print(f"{clf.YELLOW}Some devices are offline. The system will attempt to reconnect automatically.{clf.RESET}")

        if stop_event.is_set():
            break

        wait_time = 5 if show_status else 20
        stop_event.wait(wait_time)

def display_devices_status(devices: list[DeviceInterface]):
    print()
    print(f"{clf.LIGHTBLACK_EX}Current devices status:{clf.RESET}")
    for device in devices:
        is_conn = device.is_connected
        status = f"{clf.GREEN}online" if is_conn else f"{clf.RED}offline"
        print(str(f"{device.name}:").ljust(20), status) # เพิ่ม ljust
    print()

def reconnect_devices(devices: list[DeviceInterface]):
    print()
    print(f"{clf.LIGHTBLACK_EX}Attempting manual reconnect for all {len(devices)} devices...{clf.RESET}")
    threads = []
    for device in devices:
        thread = threading.Thread(target=device.reconnect, name=f"Reconnect-{device.name}")
        threads.append(thread)
        thread.start()

    print(f"{clf.LIGHTBLACK_EX}Manual reconnect process initiated.{clf.RESET}")
    time.sleep(2)
    display_devices_status(devices)


stop_event = threading.Event()
show_status = False
capture = False

def toggle_status_thread():
    global show_status
    show_status = not show_status
    terminal_logging(f"Status monitoring {clf.CYAN}{'enabled' if show_status else 'disabled'}{clf.RESET} (Updates every {'5' if show_status else '20'} sec)")

def terminate():
    global capture, show_status

    terminal_logging(f"{clf.YELLOW}Stopping the program...{clf.RESET}")
    capture = False
    stop_event.set()

def print_help():
    print()
    print(f"{APP_NAME} key commands.")
    print(f" {clf.LIGHTWHITE_EX}v{clf.RESET}   Open vscode in this path")
    print(f" {clf.LIGHTWHITE_EX}o{clf.RESET}   Open this path folder")
    print(f" {clf.LIGHTWHITE_EX}l{clf.RESET}   Open log folder")
    print(f" {clf.LIGHTWHITE_EX}h{clf.RESET}   Show this help message")
    print(f" {clf.LIGHTWHITE_EX}p{clf.RESET}   Display current devices status")
    print(f" {clf.LIGHTWHITE_EX}s{clf.RESET}   Toggle continuous status monitoring") # เพิ่ม key 's'
    print(f" {clf.LIGHTWHITE_EX}c{clf.RESET}   Clear the screen")
    print(f" {clf.LIGHTWHITE_EX}r{clf.RESET}   Manually attempt to reconnect all devices")
    print(f" {clf.LIGHTWHITE_EX}q{clf.RESET}   Quit (terminate connections and quit the program)")
    print()
    print(f"{clf.YELLOW}Press CTRL+C to quit{clf.RESET}")
    print()

print_help()

try:
    import requests
except ImportError:
    terminal_logging(f"{clf.RED}Error: 'requests' library not found.{clf.RESET}")
    terminal_logging("Please install it using: pip install requests")
    sys.exit(1)

try:
    threads: list[threading.Thread] = []
    for device in devices:
        thread = threading.Thread(target=capture_attendance, args=(device,), name=device.name)
        threads.append(thread)

    terminal_logging(f"{clf.LIGHTBLACK_EX}Starting capture threads...{clf.RESET}")

    capture = True

    status_thread = threading.Thread(target=monitor_devices_status, args=(devices,), name="StatusMonitor")
    status_thread.daemon = True
    status_thread.start()
    terminal_logging(f"Status monitoring initially {clf.CYAN}{'enabled' if show_status else 'disabled'}{clf.RESET} (Press 's' to toggle)")


    for thread in threads:
        thread.start()
        time.sleep(0.2)

    while True:
        if not any(t.is_alive() for t in threads) and not capture:
             terminal_logging(f"{clf.MAGENTA}All capture threads have stopped.{clf.RESET}")
             break

        if msvcrt.kbhit():
            try:
                key: int = ord(msvcrt.getch())
            except Exception:
                time.sleep(0.1)
                continue

            match key:
                case 118: # v
                    os.system("code .")
                case 111: # o
                    os.system("start .")
                case 108: # l
                    try:
                        os.startfile(os.path.join(CWD, LOG_AT))
                    except Exception as e:
                         terminal_logging(f"{clf.RED}Could not open log folder{clf.RESET}: {e}")
                case 104: # h
                    print_help()
                case 112: # p
                    display_devices_status(devices)
                case 115: # s (Toggle Status Monitoring)
                    toggle_status_thread()
                case 113: # q
                    terminate()
                    break
                case 114: # r
                    reconnect_devices(devices)
                case 99: # c
                    os.system("cls")
                case 3: # ctrl + c
                    terminal_logging(f"{clf.YELLOW}CTRL+C detected.{clf.RESET}")
                    terminate()
                    break # ออกจาก main loop
                case _:
                    pass
        else:
            stop_event.wait(0.1)
        if stop_event.is_set():
            break


except KeyboardInterrupt:
    terminal_logging(f"{clf.LIGHTBLACK_EX}Terminated by user (KeyboardInterrupt)")
    terminate()

finally:
    terminal_logging(f"{clf.LIGHTBLACK_EX}Waiting for threads to finish...{clf.RESET}")
    for thread in threads:
        thread.join(timeout=5)

    terminal_logging(f"{clf.MAGENTA}Program finished.{clf.RESET}")
    cl.deinit()