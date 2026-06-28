import streamlit as st
import pandas as pd
import plotly.express as px

st.set_page_config(page_title="카페 VoC 대시보드", layout="centered")

st.title("☕ 카페 VoC 한 화면")
st.caption("고객 피드백 분류 및 급한 불만 TOP 3")

df = pd.read_csv("step2_classified.csv", dtype={"별점": "object"})

# ── 유형별 개수 ──────────────────────────────────────────
st.subheader("📊 유형별 피드백 개수")

type_counts = df["유형"].value_counts().reset_index()
type_counts.columns = ["유형", "건수"]
type_counts = type_counts.sort_values("건수", ascending=False)

fig = px.bar(
    type_counts,
    x="유형",
    y="건수",
    color_discrete_sequence=["#FF6B6B"],
    hover_data={"건수": True},
)
fig.update_layout(
    xaxis_tickangle=0,
    xaxis_title=None,
    yaxis_title=None,
    showlegend=False,
    margin=dict(t=20, b=20, l=50),
)
fig.add_annotation(
    x=-0.07, y=0.5,
    xref="paper", yref="paper",
    text="건<br>수",
    showarrow=False,
    textangle=0,
    font=dict(size=14),
)
st.plotly_chart(fig, use_container_width=True)

st.divider()

# ── TOP 3 급한 불만 ──────────────────────────────────────
st.subheader("🚨 가장 급한 불만 TOP 3")
st.caption("기준: 재방문 위협도 우선 → 동일 조건에서 별점 낮을수록 가중치")

# 재방문 위협도 점수 (매우높음=4, 높음=3, 중간=2, 낮음=1)
urgency_map = {
    13: 4,  # 포인트 미적립 + 환불 요구
    21: 4,  # 직원 주문 실수 두 번
    6:  3,  # 20분 대기, 별점 1
    8:  3,  # 진동벨 불량, 음료 식음
    18: 3,  # 가격 부담
    10: 2,  # 와이파이 끊김
    3:  2,  # 앱 오류
    7:  2,  # 자리 좁음
    1:  1,  # 라떼 너무 달음
    15: 1,  # 화장실 멀음
}

complaints = df[(df["유형"] == "불만") & (df["감정"] == "부정")].copy()
complaints["위협도"] = complaints["id"].map(urgency_map)

# 별점: 없으면 중간값 2.5로 처리 (별점 있는 것보다 살짝 낮은 우선순위)
complaints["별점_수치"] = pd.to_numeric(complaints["별점"], errors="coerce").fillna(2.5)

# 정렬: 위협도 내림차순 → 별점 오름차순 (낮을수록 가중치)
complaints = complaints.sort_values(["위협도", "별점_수치"], ascending=[False, True])
top3 = complaints.head(3).reset_index(drop=True)

rank_labels = ["🥇 1위", "🥈 2위", "🥉 3위"]
border_colors = ["#FF4444", "#FF8C00", "#FFC107"]

for i, row in top3.iterrows():
    star_display = f"⭐ {int(float(row['별점_수치']))}점" if row['별점'] != '' and pd.notna(row['별점']) else "⭐ 별점 없음"
    urgency_label = {4: "매우 높음 🔴", 3: "높음 🟠", 2: "중간 🟡", 1: "낮음 🟢"}.get(int(row["위협도"]), "")

    st.markdown(f"""
<div style="border-left: 5px solid {border_colors[i]}; padding: 12px 16px; margin-bottom: 12px; background-color: #1a1a1a; border-radius: 4px;">
    <div style="font-size: 13px; color: #aaa; margin-bottom: 4px;">{rank_labels[i]} &nbsp;|&nbsp; {row['받은날짜']} &nbsp;|&nbsp; {row['경로']} &nbsp;|&nbsp; {star_display}</div>
    <div style="font-size: 16px; font-weight: bold; color: #fff; margin-bottom: 6px;">"{row['내용']}"</div>
    <div style="font-size: 12px; color: #bbb;">재방문 위협도: {urgency_label}</div>
</div>
""", unsafe_allow_html=True)

st.divider()
st.caption("💡 급한 불만 기준: 재방문 위협도(금전 피해·반복 실수·직접 불쾌 경험 순) → 동일 조건에서 별점 낮을수록 우선")
