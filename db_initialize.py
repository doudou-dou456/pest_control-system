import sqlite3
import pandas as pd
from datetime import datetime

# 1. 连接数据库（不存在则自动创建）
conn = sqlite3.connect('pest_control.db')
cursor = conn.cursor()

# 2. 创建数据表（设备表、客户表、预警数据表）
# 设备表：存储白蚁/蚊子监测设备信息
cursor.execute('''
CREATE TABLE IF NOT EXISTS devices (
    device_id TEXT PRIMARY KEY,
    device_type TEXT NOT NULL,
    location TEXT NOT NULL,
    status TEXT DEFAULT 'offline',
    last_update TEXT
)
''')

# 客户表：存储商业/居民客户信息
cursor.execute('''
CREATE TABLE IF NOT EXISTS customers (
    customer_id TEXT PRIMARY KEY,
    customer_type TEXT NOT NULL,  
    name TEXT NOT NULL,           
    address TEXT NOT NULL,        
    package_type TEXT NOT NULL,
    join_date TEXT NOT NULL       
)
''')

# 预警数据表：存储设备采集的监测数据与风险等级
cursor.execute('''
CREATE TABLE IF NOT EXISTS pest_data (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    device_id TEXT NOT NULL,
    timestamp TEXT NOT NULL,     
    temperature REAL,            
    humidity REAL,     
    pest_count INTEGER,      
    risk_level TEXT,          
    FOREIGN KEY (device_id) REFERENCES devices(device_id)
)
''')

# 3. 插入测试数据（便于后续调试）
# 插入2台设备数据
test_devices = [
    ('TERM-001', 'termite', '景洪市XX小区1号楼', 'online', '2024-10-16 09:00:00'),
    ('MOS-001', 'mosquito', '景洪市XX工业园A区', 'online', '2024-10-16 09:00:00')
]
cursor.executemany('INSERT OR IGNORE INTO devices VALUES (?, ?, ?, ?, ?)', test_devices)

# 插入2个客户数据
test_customers = [
    ('BUS-001', 'business', '景洪市XX工业园管理处', '景洪市XX路88号', '商业基础套餐', '2024-09-01'),
    ('RES-001', 'residential', '张先生', '景洪市XX小区1号楼301', '居民进阶套餐', '2024-09-15')
]
cursor.executemany('INSERT OR IGNORE INTO customers VALUES (?, ?, ?, ?, ?, ?)', test_customers)

# 插入7天的设备监测数据（模拟）
test_pest_data = [
    ('TERM-001', '2024-10-10 09:00', 26.5, 72, 5, '低'),
    ('TERM-001', '2024-10-11 09:00', 27.2, 75, 8, '低'),
    ('TERM-001', '2024-10-12 09:00', 28.1, 78, 12, '中'),
    ('TERM-001', '2024-10-13 09:00', 28.5, 80, 15, '中'),
    ('TERM-001', '2024-10-14 09:00', 27.8, 76, 10, '中'),
    ('MOS-001', '2024-10-10 09:00', 29.0, 70, 35, '低'),
    ('MOS-001', '2024-10-11 09:00', 30.2, 73, 42, '低'),
    ('MOS-001', '2024-10-12 09:00', 31.5, 76, 55, '高'),
    ('MOS-001', '2024-10-13 09:00', 32.0, 78, 63, '高'),
    ('MOS-001', '2024-10-14 09:00', 30.8, 75, 48, '中')
]
cursor.executemany('INSERT OR IGNORE INTO pest_data VALUES (NULL, ?, ?, ?, ?, ?, ?)', test_pest_data)

# 4. 提交保存并关闭数据库
conn.commit()
conn.close()
print("数据库创建完成！已生成pest_control.db文件，包含测试数据。")
