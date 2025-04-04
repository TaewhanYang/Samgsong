
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="요양원 청구 마법사", layout="wide")
st.title("🧙‍♂️ 요양원 청구 마법사")
st.write("청구 데이터를 자동으로 요양원별로 분리하고, 손쉽게 청구서 엑셀 파일을 만들어드립니다.")

uploaded_file = st.file_uploader("1. 청구 엑셀 파일을 업로드해주세요", type=["xlsx"])

if uploaded_file:
    df_raw = pd.read_excel(uploaded_file, skiprows=3)
    df_raw.columns = df_raw.columns.str.strip()

    st.success("파일 업로드 완료! 미리보기:")
    st.dataframe(df_raw.head())

    try:
        df = df_raw[["요양원명", "고객이름", "주민등록번호", "내방일▽", "요양급여액", "비급여액"]].dropna(subset=["요양원명"])
        df["요양급여액"] = pd.to_numeric(df["요양급여액"], errors='coerce')
        df["비급여액"] = pd.to_numeric(df["비급여액"], errors='coerce')

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            for center, group in df.groupby("요양원명"):
                group_sorted = group.sort_values(by="내방일▽")
                group_sorted.to_excel(writer, sheet_name=center[:31], index=False)
        output.seek(0)

        st.download_button("2. 요양원별 청구서 다운로드", data=output, file_name="요양원별_청구_자동분리.xlsx")

    except Exception as e:
        st.error(f"오류 발생: {e}")
