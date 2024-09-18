import streamlit as st
from streamlit_option_menu import option_menu
from streamlit_extras.card import card
from streamlit_extras.metric_cards import style_metric_cards
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import io
import base64

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

# 添加自定义CSS样式
def local_css(file_name):
    with open(file_name, "r", encoding="utf-8") as f:
        st.markdown(f'<style>{f.read()}</style>', unsafe_allow_html=True)

# 创建卡片组件
def create_card(title, content):
    card_html = f"""
    <div class="card">
        <h3>{title}</h3>
        <p>{content}</p>
    </div>
    """
    return st.markdown(card_html, unsafe_allow_html=True)

def read_file(file):
    file_extension = file.name.split('.')[-1].lower()
    if file_extension == 'csv':
        try:
            return pd.read_csv(file, encoding='utf-8')
        except UnicodeDecodeError:
            return pd.read_csv(file, encoding='gb18030')
    elif file_extension == 'xlsx' or file_extension == 'xls':
        return pd.read_excel(file)
    elif file_extension == 'json':
        return pd.read_json(file)
    else:
        st.error(f"不支持的文件格式：{file_extension}")
        return None

# 添加一个函数来创建可下载的图表链接
def get_image_download_link(fig, filename, text):
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=300, bbox_inches='tight')
    buf.seek(0)
    b64 = base64.b64encode(buf.getvalue()).decode()
    href = f'<a href="data:image/png;base64,{b64}" download="{filename}">{text}</a>'
    return href

def main():
    st.set_page_config(layout="wide", page_title="数据分析工具", page_icon="📊")
    
    # 侧边栏导航
    with st.sidebar:
        selected = option_menu(
            menu_title="主菜单",
            options=["数据概览", "数据清洗", "数据分析", "可视化", "高级分析"],
            icons=["table", "tools", "bar-chart", "graph-up", "gear-fill"],
            menu_icon="cast",
            default_index=0,
        )
    
    # 主内容区
    if selected == "数据概览":
        data_overview()
    elif selected == "数据清洗":
        data_cleaning()
    elif selected == "数据分析":
        data_analysis()
    elif selected == "可视化":
        data_visualization()
    elif selected == "高级分析":
        advanced_analysis()

def data_overview():
    st.title("数据概览")
    uploaded_file = st.file_uploader("选择文件", type=["csv", "xlsx", "xls", "json"])
    
    if uploaded_file is not None:
        data = read_file(uploaded_file)
        if data is not None:
            st.success("文件读取成功")
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("行数", data.shape[0])
            with col2:
                st.metric("列数", data.shape[1])
            with col3:
                st.metric("缺失值数", data.isnull().sum().sum())
            
            style_metric_cards()
            
            st.subheader("数据预览")
            st.dataframe(data.head())
            
            st.subheader("数据类型")
            st.dataframe(data.dtypes)
            
            st.session_state['data'] = data

def data_cleaning():
    st.title("数据清洗")
    if 'data' not in st.session_state:
        st.warning("请先在数据概览页面上传数据")
        return
    
    data = st.session_state['data']
    
    st.subheader("删除重复行")
    if st.button("删除重复行"):
        original_rows = data.shape[0]
        data = data.drop_duplicates()
        st.success(f"删除了 {original_rows - data.shape[0]} 行重复数据")
    
    st.subheader("处理缺失值")
    missing_columns = data.columns[data.isnull().any()].tolist()
    for column in missing_columns:
        method = st.selectbox(f"选择处理 {column} 缺失值的方法", ["保持不变", "删除", "填充平均值", "填充中位数", "填充众数"])
        if method == "删除":
            data = data.dropna(subset=[column])
        elif method == "填充平均值":
            data[column].fillna(data[column].mean(), inplace=True)
        elif method == "填充中位数":
            data[column].fillna(data[column].median(), inplace=True)
        elif method == "填充众数":
            data[column].fillna(data[column].mode()[0], inplace=True)
    
    st.session_state['data'] = data
    st.success("数据清洗完成")

def data_analysis():
    st.title("数据分析")
    if 'data' not in st.session_state:
        st.warning("请先在数据概览页面上传数据")
        return
    
    data = st.session_state['data']
    
    st.subheader("描述性统计")
    st.dataframe(data.describe())
    
    st.subheader("相关性分析")
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    corr_matrix = data[numeric_columns].corr()
    fig = px.imshow(corr_matrix, text_auto=True, aspect="auto")
    st.plotly_chart(fig, use_container_width=True)

def data_visualization():
    st.title("数据可视化")
    if 'data' not in st.session_state:
        st.warning("请先在数据概览页面上传数据")
        return
    
    data = st.session_state['data']
    
    chart_type = st.selectbox("选择图表类型", ["散点图", "线图", "柱状图", "箱线图", "直方图", "饼图"])
    
    numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
    categorical_columns = data.select_dtypes(include=['object']).columns
    
    if chart_type in ["散点图", "线图", "柱状图"]:
        x_column = st.selectbox("选择X轴", data.columns)
        y_column = st.selectbox("选择Y轴", numeric_columns)
        color_column = st.selectbox("选择颜色列（可选）", ["无"] + list(categorical_columns))
        
        if chart_type == "散点图":
            fig = px.scatter(data, x=x_column, y=y_column, color=color_column if color_column != "无" else None)
        elif chart_type == "线图":
            fig = px.line(data, x=x_column, y=y_column, color=color_column if color_column != "无" else None)
        else:  # 柱状图
            fig = px.bar(data, x=x_column, y=y_column, color=color_column if color_column != "无" else None)
    
    elif chart_type in ["箱线图", "直方图"]:
        column = st.selectbox("选择列", numeric_columns)
        if chart_type == "箱线图":
            fig = px.box(data, y=column)
        else:  # 直方图
            fig = px.histogram(data, x=column)
    
    else:  # 饼图
        column = st.selectbox("选择列", categorical_columns)
        fig = px.pie(data, names=column, values=data[column].value_counts())
    
    st.plotly_chart(fig, use_container_width=True)

def advanced_analysis():
    st.title("高级分析")
    if 'data' not in st.session_state:
        st.warning("请先在数据概览页面上传数据")
        return
    
    data = st.session_state['data']
    
    st.subheader("数据分组和聚合")
    group_column = st.selectbox("选择分组列", data.columns)
    agg_column = st.selectbox("选择聚合列", data.select_dtypes(include=['float64', 'int64']).columns)
    agg_function = st.selectbox("选择聚合函数", ["平均值", "总和", "最大值", "最小值"])
    
    agg_dict = {"平均值": "mean", "总和": "sum", "最大值": "max", "最小值": "min"}
    grouped_data = data.groupby(group_column)[agg_column].agg(agg_dict[agg_function]).reset_index()
    
    st.write("分组聚合结果：")
    st.dataframe(grouped_data)
    
    fig = px.bar(grouped_data, x=group_column, y=agg_column, title=f"{group_column} 分组的 {agg_column} {agg_function}")
    st.plotly_chart(fig, use_container_width=True)

if __name__ == '__main__':
    main()