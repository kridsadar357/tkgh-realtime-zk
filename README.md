 
#### ภาษาไทย
# TKGH Group Realtime-ZK (No DB - Messaging API)

## คำอธิบาย
โปรแกรมนี้ใช้สำหรับดึงข้อมูลการสแกนลายนิ้วมือจากเครื่อง ZK ในแบบเรียลไทม์ และส่งการแจ้งเตือนผ่าน Messaging API โดยไม่ต้องใช้ฐานข้อมูล รองรับการบันทึกข้อมูลลงไฟล์ log และการตรวจสอบสถานะอุปกรณ์

## ความต้องการของระบบ
- Python 3.x
- ไลบรารี: `colorama`, `requests`, `zk`, `pyinstaller`
- การเชื่อมต่อกับเครื่อง ZK ผ่าน IP และ Port
- Messaging API Token และ Target User ID

## การติดตั้ง
1. ติดตั้ง Python 3.x
2. รันคำสั่งเพื่อติดตั้งไลบรารี: pip install -r requirements.txt

3. แก้ไขไฟล์โค้ด:
- ใส่ IP และ Port ของเครื่อง ZK ใน `__devices__`
- ใส่ `LINE_NOTIFY_TOKEN` และ `TARGET_USER_ID` ในส่วนที่กำหนด

## การใช้งาน
1. รันโปรแกรม: python main2.py
2. คำสั่งในโปรแกรม:
- `v`: เปิด VS Code
- `o`: เปิดโฟลเดอร์ปัจจุบัน
- `l`: เปิดโฟลเดอร์ log
- `h`: แสดงคำสั่งช่วยเหลือ
- `p`: แสดงสถานะอุปกรณ์
- `s`: เปิด/ปิดการตรวจสอบสถานะต่อเนื่อง
- `r`: พยายามเชื่อมต่ออุปกรณ์ใหม่
- `q`: ออกจากโปรแกรม
- `c`: ล้างหน้าจอ

## การสร้างไฟล์ปฏิบัติการด้วย PyInstaller
1. รันคำสั่ง: pyinstaller --onefile script.py

2. ไฟล์ปฏิบัติการจะอยู่ในโฟลเดอร์ `dist`

## การตั้งค่า Task Scheduler

### บน Windows
1. เปิด Task Scheduler
2. สร้าง Task ใหม่:
- General: ตั้งชื่อ เช่น "Run ZK Script"
- Trigger: ตั้งเวลาเริ่มต้น (เช่น ทุกวัน 8:00 น.)
- Action: เลือก "Start a program"
  - Program/script: ระบุ path ไปที่ `python.exe` หรือไฟล์ `.exe` ที่สร้างจาก PyInstaller
  - Add arguments: `script.py` (ถ้าใช้ Python)
  - Start in: ระบุโฟลเดอร์ที่มีสคริปต์
3. บันทึกและทดสอบ

### บน Linux
1. เปิด Terminal
2. แก้ไข crontab: crontab -e
3. เพิ่มบรรทัด (เช่น รันทุกวัน 8:00 น.): 0 8 * * * /usr/bin/python3 /path/to/script.py
หรือถ้าใช้ไฟล์ `.exe` จาก PyInstaller: 0 8 * * * /path/to/script
4. บันทึกและตรวจสอบด้วย: crontab -l

## หมายเหตุ
- โค้ดนี้ไม่ได้มีไว้เพื่อการจำหน่าย
- ผู้ใดที่นำโค้ดนี้ไปจำหน่ายโดยไม่ได้รับอนุญาต จะถูกดำเนินคดีตามกฎหมาย
---
## สนับสนุนค่ากาแฟ
หากคุณชื่นชอบโปรเจกต์นี้ สามารถสนับสนุนค่ากาแฟได้ที่:
หมายเลขบัญชี: 0288607230
ธนาคาร: กสิกรไทย
ชื่อบัญชี: Kridsadar Ngankhayan


#### English
# PNW Realtime-ZK (No DB - LINE Notify)

## Description
This program retrieves real-time fingerprint scan data from ZK devices and sends notifications via LINE Notify without requiring a database. It supports logging data to files and monitoring device status.

## System Requirements
- Python 3.x
- Libraries: `colorama`, `requests`, `zk`, `pyinstaller`
- Connection to ZK devices via IP and Port
- LINE Notify Token and Target User ID

## Installation
1. Install Python 3.x
2. Install required libraries: pip install -r requirements.txt
3. Edit the code:
- Add ZK device IP and Port in `__devices__`
- Set `LINE_NOTIFY_TOKEN` and `TARGET_USER_ID` in the designated sections

## Usage
1. Run the program: python main2.py
2. Program commands:
- `v`: Open VS Code
- `o`: Open current folder
- `l`: Open log folder
- `h`: Show help message
- `p`: Display device status
- `s`: Toggle continuous status monitoring
- `r`: Manually reconnect devices
- `q`: Quit the program
- `c`: Clear the screen

## Building Executable with PyInstaller
1. Run the command: pyinstaller --onefile script.py
2. The executable will be in the `dist` folder

## Setting Up Task Scheduler

### On Windows
1. Open Task Scheduler
2. Create a new Task:
- General: Name it, e.g., "Run ZK Script"
- Trigger: Set start time (e.g., daily at 8:00 AM)
- Action: Select "Start a program"
  - Program/script: Specify path to `python.exe` or the `.exe` file from PyInstaller
  - Add arguments: `script.py` (if using Python)
  - Start in: Specify the script’s folder
3. Save and test

### On Linux
1. Open Terminal
2. Edit crontab: crontab -e
3. Add a line (e.g., run daily at 8:00 AM): 0 8 * * * /usr/bin/python3 /path/to/script.py
Or if using a PyInstaller `.exe`: 0 8 * * * /path/to/script
4. Save and verify with: crontab -l

## Note
- This code is not intended for sale.
- Anyone who sells this code without permission will face legal action.

## Support a Coffee
If you like this project, you can support me by buying a coffee:

Account Number: 0288607230
Bank: Kasikorn Thai
Account Name: Kridsadar Ngankhayan
