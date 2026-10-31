import sqlite3
import streamlit as st

# ของเดิม
import libsql_experimental as libsql
# ของใหม่ (Turso Cloud)
# ของใหม่
# import libsql
TURSO_URL = "libsql://dss-tokens-db-konsaelau-oss.aws-ap-southeast-1.turso.io"
TURSO_TOKEN = "eyJhbGciOiJFZERTQSIsInR5cCI6IkpXVCJ9.eyJhIjoicnciLCJpYXQiOjE3OTM0NDQ2MDUsImlkIjoiMDFhMTkxOWYtNmUwMS03MjY3LTg4NDUtMGI5YzllMjhlZThhIiwia2lkIjoidlBGRVZWTVhKQ3pKSk50bWJjTTdZTzlOX3lqMG5ONjhHOXBlTkFpbDNXQSIsInJpZCI6Ijk4ZTI2ZmY3LTFjNTMtNDc5MS1iMWJkLWRhMThkYzNjMDc5ZSJ9.HV0xLkLhnRabAvhf7Hv7D-KcUhYho5ue7kLX3R772ZlMucKNOIY12y6O-aGNW1KCHUitxYzLHxO0h0gPDoF2BQ"

#DB_FILE = "giftshop_tokens.db"

st.set_page_config(
    page_title="DSS Token Wallet - เช็ก Token สะสม",
    page_icon="🪙",
    layout="centered",
)

st.title("👛 กระเป๋า DSS Community Token")
st.caption("เช็กยอด Token ส่วนลดและประวัติการใช้งานด้วยเบอร์โทรศัพท์")

phone = st.text_input("📱 กรอกเบอร์โทรศัพท์ที่ใช้สะสม Token", max_chars=10)

if phone:
    conn = libsql.connect(database=TURSO_URL, auth_token=TURSO_TOKEN)
    c = conn.cursor()

    # ดึงข้อมูลลูกค้า
    c.execute(
        "SELECT name, token_balance FROM customers WHERE phone = ?", (phone,)
    )
    cust = c.fetchone()

    if cust:
        name = cust[0] or "คุณลูกค้า"
        balance = cust[1] or 0

        # แสดงการ์ดสะสม Token
        st.success(f"🎉 ยินดีต้อนรับ **{name}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🪙 Token คงเหลือ", f"{balance} Token")
        with col2:
            # ตามกติกา 5 Token = ส่วนลด 25 บาท (คิดเป็น Token ละ 5 บาท)
            discount_val = balance * 5
            st.metric("💡 มูลค่าส่วนลดสะสม", f"{discount_val} บาท")

        st.markdown("---")
        st.markdown("### 📜 ประวัติรายการรับ/ใช้ Token")

        # ดึงเฉพาะรายการที่ไม่โดน Void
        c.execute(
            """
            SELECT type, amount, note, created_at 
            FROM transactions 
            WHERE phone = ? AND (is_void = 0 OR is_void IS NULL) 
            ORDER BY id DESC LIMIT 10
        """,
            (phone,),
        )
        history = c.fetchall()

        if history:
            for item in history:
                t_type = (
                    "🟢 ได้รับ Token"
                    if item[0] == "EARN"
                    else "🔴 ใช้ Token ส่วนลด"
                )
                st.write(
                    f"• **[{item[3][:10]}]** {t_type} `{item[1]}` Token — *(หมายเหตุ: {item[2]})*"
                )
        else:
            st.caption("ยังไม่มีประวัติการใช้งาน")

    else:
        st.warning(
            "❌ ไม่พบเบอร์โทรศัพท์นี้ในระบบ (หากสั่งซื้อสินค้าแล้ว กรุณาแจ้งแอดมินเพื่อลงทะเบียน)"
        )

    conn.close()