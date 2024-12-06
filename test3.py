import streamlit as st
import pymysql
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import font_manager, rc

font_path = "C:/Windows/Fonts/malgun.ttf"  # Malgun Gothic 경로
font_prop = font_manager.FontProperties(fname=font_path)
rc('font', family=font_prop.get_name())

# Database connection
dbConn = pymysql.connect(user='root', passwd='1234', host='localhost', db='insu', charset='utf8')
cursor = dbConn.cursor(pymysql.cursors.DictCursor)

def query(sql, params=None):
    if params:
        cursor.execute(sql, params)
    else:
        cursor.execute(sql)
    return cursor.fetchall()

# Streamlit App Title
st.title("보험 데이터 조회 및 분석 시스템")

# Sidebar for filtering options
st.sidebar.header("필터 옵션")
selected_tab = st.sidebar.radio("탭 선택", ["고객 데이터", "계약 데이터", "청구 데이터"])

# Tab: 고객 데이터 조회
if selected_tab == "고객 데이터":
    st.subheader("고객 데이터 조회")
    
    # Filters
    sex_filter = st.sidebar.selectbox("성별 선택", options=["전체", "남성(1)", "여성(2)"])
    age_range = st.sidebar.slider("연령대 선택", min_value=18, max_value=80, value=(20, 50))
    
    # Construct SQL query
    sql = "SELECT * FROM cust WHERE 1=1"
    params = []
    if sex_filter != "전체":
        sql += " AND SEX = %s"
        params.append(int(sex_filter[-2]))
    sql += " AND AGE BETWEEN %s AND %s"
    params.extend(age_range)
    
    # Execute query and display data
    cust_data = pd.DataFrame(query(sql, tuple(params)))
    st.dataframe(cust_data)
    
    # Visualization
    if st.checkbox("고객 연령 분포 보기"):
        fig, ax = plt.subplots()
        cust_age_dist = cust_data['AGE'].value_counts().sort_index()
        ax.bar(cust_age_dist.index.astype(str), cust_age_dist.values)
        ax.set_title("고객 연령 분포")
        ax.set_xlabel("연령")
        ax.set_ylabel("고객 수")
        st.pyplot(fig)

# Tab: 계약 데이터 조회
elif selected_tab == "계약 데이터":
    st.subheader("계약 데이터 조회")
    
    # Filters
    contract_status = st.sidebar.multiselect("계약 상태 선택", options=["1", "2", "3", "4", "9", "A", "B", "C", "D", "E", "G", "H", "I", "J", "L"])
    
    # Construct SQL query
    sql = "SELECT * FROM cntt WHERE 1=1"
    params = []
    if contract_status:
        placeholders = ', '.join(['%s'] * len(contract_status))
        sql += f" AND CNTT_STAT_CODE IN ({placeholders})"
        params.extend(contract_status)
    
    # Execute query and display data
    cntt_data = pd.DataFrame(query(sql, tuple(params) if params else None))
    st.dataframe(cntt_data)
    
    # Visualization
    if st.checkbox("계약 상태 분포 보기"):
        fig, ax = plt.subplots()
        cntt_status_dist = cntt_data['CNTT_STAT_CODE'].value_counts()
        ax.pie(cntt_status_dist.values, labels=cntt_status_dist.index, autopct='%1.1f%%')
        ax.set_title("계약 상태 분포")
        st.pyplot(fig)

# Tab: 청구 데이터 조회
elif selected_tab == "청구 데이터":
    st.subheader("청구 데이터 조회")
    
    # Filters
    accident_type = st.sidebar.multiselect("사고 구분 선택", options=["1", "2", "3"])
    
    # Construct SQL query
    sql = "SELECT * FROM claim WHERE 1=1"
    params = []
    if accident_type:
        placeholders = ', '.join(['%s'] * len(accident_type))
        sql += f" AND ACCI_DVSN IN ({placeholders})"
        params.extend(accident_type)
    
    # Execute query and display data
    claim_data = pd.DataFrame(query(sql, tuple(params) if params else None))
    st.dataframe(claim_data)
    
    # Visualization
    if st.checkbox("청구 금액 분포 보기"):
        fig, ax = plt.subplots()
        ax.hist(claim_data['DMND_AMT'], bins=20)
        ax.set_title("청구 금액 분포")
        ax.set_xlabel("청구 금액")
        ax.set_ylabel("빈도")
        st.pyplot(fig)

# 고객 ID로 검색 기능
st.sidebar.header("고객 ID로 검색")
search_id = st.sidebar.text_input("고객 ID 입력")
if st.sidebar.button("검색"):
    # 고객 정보 조회
    cust_info = pd.DataFrame(query("SELECT * FROM cust WHERE CUST_ID = %s", (search_id,)))
    if not cust_info.empty:
        st.subheader("고객 정보")
        st.dataframe(cust_info)
        
        # 계약 정보 조회
        cntt_info = pd.DataFrame(query("SELECT * FROM cntt WHERE CUST_ID = %s", (search_id,)))
        if not cntt_info.empty:
            st.subheader("계약 정보")
            st.dataframe(cntt_info)
        
        # 청구 정보 조회
        claim_info = pd.DataFrame(query("SELECT * FROM claim WHERE CUST_ID = %s", (search_id,)))
        if not claim_info.empty:
            st.subheader("청구 정보")
            st.dataframe(claim_info)
    else:
        st.warning("해당 고객 ID를 찾을 수 없습니다.")

# Close database connection
#dbConn.close()