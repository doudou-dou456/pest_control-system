import streamlit as st
import sqlite3
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta

import os
# ---------------------- 1. 数据库工具函数（连接/查询） ----------------------
def get_db_connection():
        current_dir = os.path.dirname(os.path.abspath(__file__))
        # 拼接数据库文件路径
        db_path = os.path.join(current_dir, "pest_control.db")
        conn = sqlite3.connect(db_path)
        conn.row_factory = sqlite3.Row  # 支持按列名获取数据
        return conn


def fetch_data(query, params=()):
    """执行查询并返回DataFrame格式数据"""
    conn = get_db_connection()
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    return df


# ---------------------- 2. 页面布局与导航 ----------------------
st.set_page_config(
    page_title="智能虫防系统",
    page_icon="🐛",  # 这里要确保标点和语法正确
    layout="wide"
)
# 导航栏（侧边栏）
st.sidebar.title("智虫防系统")
nav_option = st.sidebar.radio(
    "请选择功能模块",
    ["设备状态监控", "虫害风险预警", "客户服务查询", "关于我们"]
)

# ---------------------- 3. 功能模块1：设备状态监控 ----------------------
if nav_option == "设备状态监控":
    st.title("📊 设备状态监控")
    st.divider()  # 分割线

    # 3.1 筛选条件（设备类型、状态）
    col1, col2 = st.columns(2)
    with col1:
        device_type = st.selectbox("选择设备类型", ["全部", "白蚁监测设备", "蚊子监测设备"])
        type_map = {"全部": "", "白蚁监测设备": "termite", "蚊子监测设备": "mosquito"}
        type_filter = type_map[device_type]
    with col2:
        device_status = st.selectbox("选择设备状态", ["全部", "在线", "离线"])
        status_map = {"全部": "", "在线": "online", "离线": "offline"}
        status_filter = status_map[device_status]

    # 3.2 查询设备数据
    query = "SELECT * FROM devices WHERE 1=1"
    params = []
    if type_filter:
        query += " AND device_type = ?"
        params.append(type_filter)
    if status_filter:
        query += " AND status = ?"
        params.append(status_filter)

    devices_df = fetch_data(query, params)
    if devices_df.empty:
        st.warning("暂无符合条件的设备数据！")
    else:
        # 格式化显示（替换英文为中文）
        devices_df["device_type"] = devices_df["device_type"].replace(
            {"termite": "白蚁监测设备", "mosquito": "蚊子监测设备"})
        devices_df["status"] = devices_df["status"].replace({"online": "在线", "offline": "离线"})
        st.dataframe(devices_df, use_container_width=True)  # 自适应宽度表格

        # 3.3 设备状态统计图表
        st.subheader("设备状态分布")
        status_count = devices_df["status"].value_counts()
        fig = px.pie(
            values=status_count.values,
            names=status_count.index,
            title="在线/离线设备占比",
            color_discrete_map={"在线": "#2E8B57", "离线": "#DC143C"}
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- 4. 功能模块2：虫害风险预警 ----------------------
elif nav_option == "虫害风险预警":
    st.title("⚠️ 虫害风险预警")
    st.divider()

    # 4.1 选择设备（查看单设备历史数据与风险）
    device_query = "SELECT device_id, device_type, location FROM devices"
    devices = fetch_data(device_query)
    if devices.empty:
        st.warning("暂无设备数据，无法查看风险预警！")
    else:
        # 设备下拉选择（显示“设备ID-类型-位置”）
        device_options = [
            f"{row['device_id']} - {row['device_type'].replace('termite', '白蚁').replace('mosquito', '蚊子')} - {row['location']}"
            for _, row in devices.iterrows()
        ]
        selected_device = st.selectbox("选择查看的设备", device_options)
        selected_device_id = selected_device.split(" - ")[0]  # 提取设备ID

        # 4.2 查询该设备的历史监测数据（近7天）
        end_date = datetime.now().strftime("%Y-%m-%d")
        start_date = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")
        pest_query = """
            SELECT timestamp, temperature, humidity, pest_count, risk_level 
            FROM pest_data 
            WHERE device_id = ? AND date(timestamp) BETWEEN ? AND ?
            ORDER BY timestamp ASC
        """
        pest_df = fetch_data(pest_query, (selected_device_id, start_date, end_date))

        if pest_df.empty:
            st.warning(f"该设备近7天无监测数据！")
        else:
            # 4.3 显示监测数据表格
            st.subheader(f"设备 {selected_device_id} - 近7天监测数据")
            st.dataframe(pest_df, use_container_width=True)

            # 4.4 绘制趋势图表（虫害数量+温湿度）
            st.subheader("虫害数量与环境参数趋势")
            fig = px.line(
                pest_df,
                x="timestamp",
                y=["pest_count", "temperature", "humidity"],
                title="虫害数量、温度、湿度变化",
                labels={"timestamp": "时间", "value": "数值", "variable": "指标"},
                color_discrete_map={
                    "pest_count": "#8B4513",
                    "temperature": "#FF4500",
                    "humidity": "#1E90FF"
                }
            )
            st.plotly_chart(fig, use_container_width=True)

            # 4.5 风险等级统计
            st.subheader("风险等级分布")
            risk_count = pest_df["risk_level"].value_counts()
            fig_risk = px.bar(
                x=risk_count.index,
                y=risk_count.values,
                title="各风险等级天数",
                color=risk_count.index,
                color_discrete_map={"低": "#32CD32", "中": "#FFD700", "高": "#FF4500"}
            )
            st.plotly_chart(fig_risk, use_container_width=True)

# ---------------------- 5. 功能模块3：客户服务查询 ----------------------
elif nav_option == "客户服务查询":
    st.title("👥 客户服务查询")
    st.divider()

    # 5.1 客户类型筛选
    customer_type = st.selectbox("选择客户类型", ["全部", "商业客户", "居民客户"])
    type_filter = {"全部": "", "商业客户": "business", "居民客户": "residential"}[customer_type]

    # 5.2 查询客户数据
    query = "SELECT * FROM customers WHERE 1=1"
    params = []
    if type_filter:
        query += " AND customer_type = ?"
        params.append(type_filter)

    customers_df = fetch_data(query, params)
    if customers_df.empty:
        st.warning("暂无符合条件的客户数据！")
    else:
        # 格式化显示（替换英文为中文）
        customers_df["customer_type"] = customers_df["customer_type"].replace(
            {"business": "商业客户", "residential": "居民客户"})
        st.dataframe(customers_df, use_container_width=True)

        # 5.3 客户套餐分布
        st.subheader("客户套餐类型分布")
        package_count = customers_df["package_type"].value_counts()
        fig = px.bar(
            x=package_count.index,
            y=package_count.values,
            title="各套餐客户数量",
            color=package_count.index,
            color_discrete_sequence=px.colors.qualitative.Pastel
        )
        st.plotly_chart(fig, use_container_width=True)

# ---------------------- 6. 功能模块4：关于我们 ----------------------
elif nav_option == "关于我们":
    st.title("🏢 关于智虫防")
    st.divider()
    st.markdown("""
    ### 项目简介
    智虫防是基于大数据技术的精准虫害防治服务平台，专注于白蚁、蚊子两类高频高损虫害，提供“提前预警、精准施策、效果追溯”的全链路服务，打破传统防治“被动响应、盲目施药”的痛点。

    ### 核心优势
    1. **全链路技术闭环**：智能监测+大数据预警+精准防治+效果追溯；
    2. **垂直场景聚焦**：针对白蚁、蚊子定制算法与方案；
    3. **数据驱动优化**：全流程数据采集，持续提升服务效果。

    ### 合作支持
    - 战略合作伙伴：景洪蚁王白蚁防治有限公司
    - 服务热线：13618813680
    - 地址：云南省西双版纳州景洪市舒邦小镇59号楼127号
    """)

# ---------------------- 7. 页脚 ----------------------
st.sidebar.markdown("""
---
**智虫防系统 v1.0**  
© 2025 生物科技害虫防治项目组  
""")