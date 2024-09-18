import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os
import io
from matplotlib import font_manager
import numpy as np
from scipy import stats
import openpyxl  # 用于读取Excel文件

# 设置中文字体
plt.rcParams['font.sans-serif'] = ['Microsoft YaHei']  # 指定默认字体为微软雅黑
plt.rcParams['axes.unicode_minus'] = False  # 解决保存图像是负号'-'显示为方块的问题

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

def main():
    st.title('数据可视化和分析工具')
    
    uploaded_file = st.file_uploader("选择文件", type=["csv", "xlsx", "xls", "json"])
    
    if uploaded_file is not None:
        data = read_file(uploaded_file)
        if data is not None:
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

            # 添加数据清洗功能
            st.subheader("数据清洗")
            if st.checkbox("删除重复行"):
                data = data.drop_duplicates()
                st.write(f"删除了 {len(data) - len(data.drop_duplicates())} 行重复数据")
            
            if st.checkbox("处理缺失值"):
                missing_columns = data.columns[data.isnull().any()].tolist()
                for column in missing_columns:
                    method = st.selectbox(f"选择处理 {column} 缺失值的方法", ["删除", "填充平均值", "填充中位数", "填充众数"])
                    if method == "删除":
                        data = data.dropna(subset=[column])
                    elif method == "填充平均值":
                        data[column].fillna(data[column].mean(), inplace=True)
                    elif method == "填充中位数":
                        data[column].fillna(data[column].median(), inplace=True)
                    elif method == "填充众数":
                        data[column].fillna(data[column].mode()[0], inplace=True)
            
            st.write("清洗后的数据：")
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
            categorical_columns = data.select_dtypes(include=['object']).columns
            
            chart_type = st.selectbox("选择图表类型", ["直方图", "箱线图", "散点图", "折线图", "条形图", "饼图", "热力图"])
            
            column_to_plot = None
            x_column = None
            y_column = None

            if chart_type in ["直方图", "箱线图", "折线图", "条形图"]:
                column_to_plot = st.selectbox("选择要可视化的列", numeric_columns)
            elif chart_type == "散点图":
                x_column = st.selectbox("选择X轴", numeric_columns)
                y_column = st.selectbox("选择Y轴", numeric_columns)
            elif chart_type == "饼图":
                column_to_plot = st.selectbox("选择要可视化的列", categorical_columns)
            elif chart_type == "热力图":
                st.write("热力图将使用所有数值列")
            
            fig, ax = plt.subplots(figsize=(10, 6))
            
            if chart_type == "直方图":
                sns.histplot(data[column_to_plot], kde=True, ax=ax)
            elif chart_type == "箱线图":
                sns.boxplot(y=data[column_to_plot], ax=ax)
            elif chart_type == "散点图":
                sns.scatterplot(x=data[x_column], y=data[y_column], ax=ax)
            elif chart_type == "折线图":
                data[column_to_plot].plot(ax=ax)
            elif chart_type == "条形图":
                data[column_to_plot].value_counts().plot(kind='bar', ax=ax)
            elif chart_type == "饼图":
                data[column_to_plot].value_counts().plot(kind='pie', autopct='%1.1f%%', ax=ax)
            elif chart_type == "热力图":
                sns.heatmap(data[numeric_columns].corr(), annot=True, cmap='coolwarm', ax=ax)
            
            plt.title(f"{chart_type}")
            if chart_type == "散点图":
                ax.set_xlabel(x_column)
                ax.set_ylabel(y_column)
            elif chart_type != "饼图" and chart_type != "热力图":
                ax.set_xlabel(column_to_plot)
                ax.set_ylabel("频率" if chart_type == "直方图" else column_to_plot)
            plt.xticks(rotation=45)
            st.pyplot(fig)

            # 相关性分析
            st.subheader("相关性分析")
            corr_matrix = data[numeric_columns].corr()
            fig, ax = plt.subplots(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', ax=ax)
            plt.title("相关性热图")
            st.pyplot(fig)

            # 高级数据分析
            st.subheader("高级数据分析")
            if st.checkbox("执行假设检验"):
                column1 = st.selectbox("选择第一个列", numeric_columns)
                column2 = st.selectbox("选择第二个列", numeric_columns)
                
                t_statistic, p_value = stats.ttest_ind(data[column1], data[column2])
                st.write(f"T检验结果：t统计量 = {t_statistic:.4f}, p值 = {p_value:.4f}")
                
                if p_value < 0.05:
                    st.write("在0.05显著性水平下，两列数据存在显著差异。")
                else:
                    st.write("在0.05显著性水平下，两列数据不存在显著差异。")

            # 数据分组和聚合功能
            st.subheader("数据分组和聚合")
            group_column = st.selectbox("选择分组列", data.columns)
            agg_column = st.selectbox("选择聚合列", numeric_columns)
            agg_function = st.selectbox("选择聚合函数", ["平均值", "总和", "最大值", "最小值"])
            
            agg_dict = {"平均值": "mean", "总和": "sum", "最大值": "max", "最小值": "min"}
            grouped_data = data.groupby(group_column)[agg_column].agg(agg_dict[agg_function]).reset_index()
            
            st.write("分组聚合结果：")
            st.write(grouped_data)
            
            # 可视化分组结果
            fig, ax = plt.subplots(figsize=(10, 6))
            sns.barplot(x=group_column, y=agg_column, data=grouped_data, ax=ax)
            plt.title(f"{group_column} 分组的 {agg_column} {agg_function}")
            plt.xticks(rotation=45)
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