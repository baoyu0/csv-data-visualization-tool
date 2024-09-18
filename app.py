import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
from matplotlib import font_manager

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

def main():
    st.title('CSV数据可视化和分析工具')
    
    uploaded_file = st.file_uploader("选择CSV文件", type="csv")
    
    if uploaded_file is not None:
        try:
            data = pd.read_csv(uploaded_file, encoding='utf-8')
        except UnicodeDecodeError:
            data = pd.read_csv(uploaded_file, encoding='gb18030')
        
        st.write("文件读取成功")
        st.write(data.head())

        # 数据过滤
        st.subheader("数据过滤")
        columns_to_filter = st.multiselect("选择要过滤的列", data.columns)
        if columns_to_filter:
            for column in columns_to_filter:
                unique_values = data[column].unique()
                selected_values = st.multiselect(f"选择 {column} 的值", unique_values)
                if selected_values:
                    data = data[data[column].isin(selected_values)]
        
        st.write("过滤后的数据：")
        st.write(data)

        # 数据分析
        st.subheader("数据分析")
        st.write(f"数据集包含 {data.shape[0]} 行和 {data.shape[1]} 列")
        st.write("数据类型：")
        st.write(data.dtypes)

        # 描述性统计
        st.subheader("描述性统计")
        st.write(data.describe())

        # 数据可视化
        st.subheader("数据可视化")
        numeric_columns = data.select_dtypes(include=['float64', 'int64']).columns
        column_to_plot = st.selectbox("选择要可视化的列", numeric_columns)
        
        chart_type = st.radio("选择图表类型", ["直方图", "箱线图", "散点图"])
        
        fig, ax = plt.subplots(figsize=(10, 6))
        if chart_type == "直方图":
            sns.histplot(data[column_to_plot], kde=True, ax=ax)
        elif chart_type == "箱线图":
            sns.boxplot(y=data[column_to_plot], ax=ax)
        else:  # 散点图
            x_column = st.selectbox("选择X轴", numeric_columns)
            sns.scatterplot(x=data[x_column], y=data[column_to_plot], ax=ax)
        
        plt.title(f"{column_to_plot} 的 {chart_type}")
        ax.set_xlabel(column_to_plot)
        ax.set_ylabel("频率" if chart_type == "直方图" else column_to_plot)
        st.pyplot(fig)

        # 相关性分析
        st.subheader("相关性分析")
        corr_matrix = data[numeric_columns].corr()
        fig, ax = plt.subplots(figsize=(10, 8))
        sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
        plt.title("相关性热图")
        st.pyplot(fig)

        # 数据导出
        st.subheader("数据导出")
        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
            data.to_excel(writer, sheet_name='Sheet1', index=False)
        output.seek(0)
        st.download_button(
            label="下载处理后的数据为Excel文件",
            data=output,
            file_name="processed_data.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )

if __name__ == '__main__':
    main()