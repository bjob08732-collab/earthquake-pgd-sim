import streamlit as st
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd

# ----------------- 1. 网页全局设置 -----------------
st.set_page_config(page_title="近断层位移模拟器", layout="wide")
st.title("近断层地表永久位移 (PGD) 空间分布模拟器")
st.markdown("本工具用于可视化不同震级和断层机制下，跨断层地表的永久位移（包含滑冲效应与上下盘效应）。")

# ----------------- 2. 侧边栏：控制面板 -----------------
st.sidebar.header("模型参数控制")
mw = st.sidebar.slider("矩震级 (Mw)", min_value=6.0, max_value=8.0, value=7.0, step=0.1)
fault_type = st.sidebar.selectbox("断层机制",
                                  ["逆冲断层 (Thrust/Reverse)", "走滑断层 (Strike-Slip)", "正断层 (Normal)"])

# ----------------- 3. 核心物理/数学模型计算 -----------------
# X轴：生成横跨断层的距离，从 -20km 到 20km (0点为断层地表迹线)
x = np.linspace(-20, 20, 500)

# 基础位移峰值经验公式 (这里采用简化指数模型演示，建议替换为你的实际拟合公式)
# 震级每增加1级，能量呈指数级放大
d_max = 10 * (2.5 ** (mw - 6.5))

# 初始化水平和竖直位移数组
v_disp = np.zeros_like(x)
h_disp = np.zeros_like(x)

# 根据不同断层机制应用不同的空间衰减函数
for i, xi in enumerate(x):
    if "逆冲断层" in fault_type:
        if xi > 0:  # 上盘 (剧烈抬升)
            v_disp[i] = d_max * np.exp(-xi / 4.0)
            h_disp[i] = -0.5 * d_max * np.exp(-xi / 4.0)
        else:  # 下盘 (轻微下沉)
            v_disp[i] = -0.1 * d_max * np.exp(xi / 4.0)
            h_disp[i] = 0.5 * d_max * np.exp(xi / 4.0)

    elif "正断层" in fault_type:
        if xi > 0:  # 上盘 (剧烈沉降)
            v_disp[i] = -d_max * np.exp(-xi / 4.0)
            h_disp[i] = 0.5 * d_max * np.exp(-xi / 4.0)
        else:  # 下盘 (轻微隆起)
            v_disp[i] = 0.1 * d_max * np.exp(xi / 4.0)
            h_disp[i] = -0.5 * d_max * np.exp(xi / 4.0)

    elif "走滑断层" in fault_type:
        v_disp[i] = 0  # 走滑断层竖直向位移极小
        # 水平向表现为典型的 Fling-step (滑冲阶跃)
        if xi > 0:
            h_disp[i] = d_max * (1 - np.exp(-xi / 5.0))
        else:
            h_disp[i] = -d_max * (1 - np.exp(xi / 5.0))

# ----------------- 4. 数据可视化绘图 -----------------
# 设置中文字体（防止乱码，如果你的电脑没有黑体可以注释掉这两行）
plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 图1：竖直向位移
ax1.plot(x, v_disp, color='#E63946', linewidth=3)
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax1.fill_between(x, v_disp, 0, alpha=0.2, color='#E63946')
ax1.set_title(f"竖直向永久位移 (Vertical PGD)", fontsize=14, fontweight='bold')
ax1.set_ylabel("位移量 (cm)", fontsize=12)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.text(-19, ax1.get_ylim()[1] * 0.8, '← 下盘 (Footwall)', fontsize=12, color='#2d3436',
         bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
ax1.text(10, ax1.get_ylim()[1] * 0.8, '上盘 (Hanging wall) →', fontsize=12, color='#2d3436',
         bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))

# 图2：水平向位移
ax2.plot(x, h_disp, color='#457B9D', linewidth=3)
ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax2.fill_between(x, h_disp, 0, alpha=0.2, color='#457B9D')
ax2.set_title(f"水平向永久位移 (Horizontal PGD)", fontsize=14, fontweight='bold')
ax2.set_xlabel("横跨断层距离 (km) [0处为断层地表迹线]", fontsize=12, fontweight='bold')
ax2.set_ylabel("位移量 (cm)", fontsize=12)
ax2.grid(True, linestyle=':', alpha=0.6)

plt.tight_layout()

# 将绘制好的图表推送到网页
st.pyplot(fig)

# ----------------- 5. 附加功能：数据展示区 -----------------
st.markdown("---")
with st.expander("查看当前参数下的空间剖面数据表"):
    df = pd.DataFrame({
        "距离_km": x,
        "竖直位移_cm": v_disp,
        "水平位移_cm": h_disp
    })
    st.dataframe(df.style.format("{:.2f}"), use_container_width=True)
