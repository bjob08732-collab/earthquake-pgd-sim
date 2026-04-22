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

import numpy as np

# ----------------- 3. 核心物理/数学模型计算 -----------------

# 1. 必须要先定义 x (横轴距离坐标)！生成从 -max_dist 到 +max_dist 的 500 个点
# 如果你没有 max_dist 变量，可以直接写死数字，比如：x = np.linspace(-30, 30, 500)
# 在网页侧边栏添加一个控制距离的滑块（默认显示 30 km）
max_dist = st.sidebar.slider("最大显示距离 (km)", 10, 100, 30)

# 然后根据滑块的值生成 x 坐标
x = np.linspace(-max_dist, max_dist, 500)

# 2. 你的真实核心回归系数 (请换成你刚才回归得出的真实数值)
C_H = {"c1": -4.5793, "c2": 1.5042, "c3": -0.8335, "c4": 0.0430, "c5": -0.1945, "h": 5.0}
C_V = {"c1": -5.2102, "c2": 1.3883, "c3": -0.7883, "c4": 0.3040, "c5": 0.0428, "h": 5.0}

# 3. 定义断层变量 (Dummy Variables)
f_rv = 1 if "逆冲" in fault_type else 0
f_nm = 1 if "正断" in fault_type else 0

# 4. 计算位移 (注意：这里修正了对数项，使用的是 ["h"] 而不是 ["c1"])
h_val = np.exp(C_H["c1"] + C_H["c2"] * mw + C_H["c3"] * np.log(np.abs(x) + C_H["h"]) + C_H["c4"] * f_rv + C_H["c5"] * f_nm)
v_val = np.exp(C_V["c1"] + C_V["c2"] * mw + C_V["c3"] * np.log(np.abs(x) + C_V["h"]) + C_V["c4"] * f_rv + C_V["c5"] * f_nm)

# 5. 上下盘方向处理
h_disp = np.where(x >= 0, h_val, -h_val)

if "逆冲" in fault_type:
    v_disp = np.where(x >= 0, v_val, -0.1 * v_val)
elif "正断" in fault_type:
    v_disp = np.where(x >= 0, -v_val, 0.1 * v_val)
else:
    v_disp = np.zeros_like(x)

# ----------------- 4. 数据可视化绘图 -----------------
# 注释掉强制使用中文黑体的设置，让云服务器使用默认英文安全字体
# plt.rcParams['font.sans-serif'] = ['SimHei', 'Arial Unicode MS']
plt.rcParams['axes.unicode_minus'] = False

fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(10, 8), sharex=True)

# 图1：竖直向位移
ax1.plot(x, v_disp, color='#E63946', linewidth=3)
ax1.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax1.fill_between(x, v_disp, 0, alpha=0.2, color='#E63946')
ax1.set_title(f"Vertical Permanent Ground Displacement (PGD)", fontsize=14, fontweight='bold')
ax1.set_ylabel("Displacement (cm)", fontsize=12)
ax1.grid(True, linestyle=':', alpha=0.6)
ax1.text(-19, ax1.get_ylim()[1]*0.8, '<- Footwall', fontsize=12, color='#2d3436', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))
ax1.text(10, ax1.get_ylim()[1]*0.8, 'Hanging Wall ->', fontsize=12, color='#2d3436', bbox=dict(facecolor='white', alpha=0.5, edgecolor='none'))

# 图2：水平向位移
ax2.plot(x, h_disp, color='#457B9D', linewidth=3)
ax2.axvline(x=0, color='gray', linestyle='--', alpha=0.7)
ax2.fill_between(x, h_disp, 0, alpha=0.2, color='#457B9D')
ax2.set_title(f"Horizontal Permanent Ground Displacement (PGD)", fontsize=14, fontweight='bold')
ax2.set_xlabel("Cross-fault Distance (km) [0 = Fault Trace]", fontsize=12, fontweight='bold')
ax2.set_ylabel("Displacement (cm)", fontsize=12)
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
