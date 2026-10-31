import sqlite3
import streamlit as st

DB_FILE = "giftshop_tokens.db"

st.set_page_config(
    page_title="DSS Token Wallet - เช็กเหรียญสะสม",
    page_icon="🪙",
    layout="centered",
)

st.title("👛 กระเป๋าเหรียญสะสม DSS Community Token")
st.caption("เช็กยอดเหรียญส่วนลดและประวัติการใช้งานด้วยเบอร์โทรศัพท์")

phone = st.text_input("📱 กรอกเบอร์โทรศัพท์ที่ใช้สะสมเหรียญ", max_chars=10)

if phone:
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()

    # ดึงข้อมูลลูกค้า
    c.execute(
        "SELECT name, token_balance FROM customers WHERE phone = ?", (phone,)
    )
    cust = c.fetchone()

    if cust:
        name = cust[0] or "คุณลูกค้า"
        balance = cust[1] or 0

        # แสดงการ์ดสะสมเหรียญ
        st.success(f"🎉 ยินดีต้อนรับ **{name}**")

        col1, col2 = st.columns(2)
        with col1:
            st.metric("🪙 เหรียญคงเหลือ", f"{balance} เหรียญ")
        with col2:
            discount_val = balance * 5  # เช่น 1 เหรียญ = ส่วนลด 5 บาท
            st.metric("💡 มูลค่าส่วนลดสะสม", f"{discount_val} บาท")

        st.markdown("---")
        st.markdown("### 📜 ประวัติรายการรับ/ใช้เหรียญ")

        c.execute(
            "SELECT type, amount, note, created_at FROM transactions WHERE phone = ? ORDER BY id DESC LIMIT 10",
            (phone,),
        )
        history = c.fetchall()

        if history:
            for item in history:
                t_type = (
                    "🟢 ได้รับเหรียญ"
                    if item[0] == "EARN"
                    else "🔴 ใช้ส่วนลด/แลกของ"
                )
                st.write(
                    f"• **[{item[3][:10]}]** {t_type} `{item[1]}` เหรียญ ({item[2]})"
                )
        else:
            st.caption("ยังไม่มีประวัติการใช้งาน")

    else:
        st.warning(
            "❌ ไม่พบเบอร์โทรศัพท์นี้ในระบบ (หากสั่งซื้อสินค้าแล้ว กรุณาแจ้งแอดมินเพื่อลงทะเบียน)"
        )

    conn.close()