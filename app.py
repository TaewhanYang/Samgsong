
import streamlit as st
import pandas as pd
import io

st.set_page_config(page_title="요양원 청구 마법사", layout="wide")
st.title("🧙‍♂️ 요양원 청구 마법사")

tab1, tab2, tab3 = st.tabs(["1. 기본테이블 업데이트", "2. 요양원 자동 매칭", "3. 청구서 생성"])

# 탭1: 기본테이블 업데이트
with tab1:
    st.subheader("📌 기본 테이블 + 신규 데이터 병합")
    base_file = st.file_uploader("기존 기본테이블 업로드", type="xlsx", key="base1")
    new_file = st.file_uploader("신규 환자 데이터 업로드", type="xlsx", key="new1")

    if base_file and new_file:
        base_df = pd.read_excel(base_file)
        new_df = pd.read_excel(new_file)

        combined_df = pd.concat([base_df, new_df])
        combined_df.drop_duplicates(subset=["고객이름", "주민등록번호"], keep="first", inplace=True)

        st.success("병합된 기본 테이블 미리보기:")
        st.dataframe(combined_df.head())

        output = io.BytesIO()
        with pd.ExcelWriter(output, engine='openpyxl') as writer:
            combined_df.to_excel(writer, index=False)
        output.seek(0)
        st.download_button("병합된 기본테이블 다운로드", data=output, file_name="기본테이블_업데이트.xlsx")

# 탭2: 요양원 자동 매칭
with tab2:
    st.subheader("📌 요양원이 비어 있는 환자 데이터를 기본 테이블 기준으로 자동 매칭")
    base_file2 = st.file_uploader("기본테이블 업로드", type="xlsx", key="base2")
    crude_file = st.file_uploader("요양원 미지정 crude 데이터 업로드", type="xlsx", key="crude")

    if base_file2 and crude_file:
        base_df = pd.read_excel(base_file2)
        crude_df = pd.read_excel(crude_file)

        merged_df = pd.merge(crude_df, base_df[["고객이름", "주민등록번호", "요양원명"]], on=["고객이름", "주민등록번호"], how="left")
        st.success("요양원명이 자동 채워진 결과:")
        st.dataframe(merged_df.head())

        output2 = io.BytesIO()
        with pd.ExcelWriter(output2, engine='openpyxl') as writer:
            merged_df.to_excel(writer, index=False)
        output2.seek(0)
        st.download_button("자동 매칭된 데이터 다운로드", data=output2, file_name="요양원_자동매칭.xlsx")

# 탭3: 청구서 생성
with tab3:
    st.subheader("📌 청구서 자동 생성")
    billing_file = st.file_uploader("자동매칭된 데이터 업로드", type="xlsx", key="final")

    if billing_file:
        df_raw = pd.read_excel(billing_file)
        df_raw["요양급여액"] = pd.to_numeric(df_raw["요양급여액"], errors='coerce')
        df_raw["비급여액"] = pd.to_numeric(df_raw["비급여액"], errors='coerce')
        df_raw["합계"] = df_raw["요양급여액"].fillna(0) + df_raw["비급여액"].fillna(0)

        output3 = io.BytesIO()
        with pd.ExcelWriter(output3, engine='openpyxl') as writer:
            # 목차 시트 생성
            writer.book.create_sheet("요양원목차", 0)
            idx = 1
            for center, group in df_raw.groupby("요양원명"):
                group_sorted = group.sort_values(by="내방일▽")
                group_sorted.to_excel(writer, sheet_name=center[:31], index=False)
                writer.sheets["요양원목차"].cell(row=idx+1, column=1).value = center
                idx += 1
        output3.seek(0)

        st.success("청구서 생성 완료! 다운로드하세요:")
        st.download_button("요양원별 청구서 다운로드", data=output3, file_name="요양원별_청구_최종.xlsx")
