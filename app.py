
import streamlit as st
import streamlit.components.v1 as components
import json
import os
from datetime import datetime, time as dt_time

st.set_page_config(
    page_title="مُجيب | المساعد الصحي",
    page_icon="💙",
    layout="wide",
    initial_sidebar_state="collapsed"
)

DATA_FILE = "mujib_medicines.json"

# ---------- ألوان واضحة ----------
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;500;600;700;800&display=swap');

html, body, [class*="css"] {
    font-family: 'Cairo', sans-serif;
    direction: rtl;
}
.stApp {
    background: #F3F6FA;
    color: #172B40;
}
.block-container {
    max-width: 1100px;
    padding-top: 1.5rem;
    padding-bottom: 3rem;
}
.hero {
    background: #173B5C;
    color: #FFFFFF;
    padding: 28px;
    border-radius: 20px;
    margin-bottom: 22px;
}
.hero h1 {
    color: #FFFFFF !important;
    font-size: 34px;
}
.hero p { color: #EAF2F9 !important; }
.card {
    background: #FFFFFF;
    border: 1px solid #D5DFE9;
    border-radius: 16px;
    padding: 20px;
    margin-bottom: 14px;
    color: #172B40;
}
.metric {
    background: #FFFFFF;
    border: 1px solid #D5DFE9;
    border-radius: 14px;
    padding: 16px;
    text-align: center;
}
.metric h2 { color: #155E75 !important; }
.small { color: #526579; font-size: 14px; }
h1, h2, h3, p, label {
    color: #172B40;
}
[data-testid="stWidgetLabel"] p {
    color: #172B40 !important;
    font-weight: 700;
}
div.stButton > button,
div.stFormSubmitButton > button {
    background: #155E75;
    color: #FFFFFF;
    border: 1px solid #155E75;
    border-radius: 10px;
    min-height: 43px;
    font-family: 'Cairo', sans-serif;
    font-weight: 700;
}
div.stButton > button:hover,
div.stFormSubmitButton > button:hover {
    background: #10485A;
    color: #FFFFFF;
    border-color: #10485A;
}
[data-testid="stTabs"] button {
    color: #172B40;
    font-family: 'Cairo', sans-serif;
}
input, textarea {
    color: #172B40 !important;
}
div[data-baseweb="select"] * {
    color: #172B40;
}
.stAlert p { color: #172B40 !important; }
</style>
""", unsafe_allow_html=True)


# ---------- حفظ الأدوية ----------
def load_medicines():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r", encoding="utf-8") as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
        except (OSError, json.JSONDecodeError):
            pass
    return []


def save_medicines():
    with open(DATA_FILE, "w", encoding="utf-8") as file:
        json.dump(
            st.session_state.medicines,
            file,
            ensure_ascii=False,
            indent=2
        )


if "medicines" not in st.session_state:
    st.session_state.medicines = load_medicines()

if "chat" not in st.session_state:
    st.session_state.chat = []

if "watch_connected" not in st.session_state:
    st.session_state.watch_connected = False


# ---------- الصوت العربي ----------
def speak_arabic(message):
    components.html(
        f"""
        <script>
        const text = {json.dumps(message, ensure_ascii=False)};
        if ('speechSynthesis' in window) {{
            window.speechSynthesis.cancel();
            const speech = new SpeechSynthesisUtterance(text);
            speech.lang = 'ar-SA';
            speech.rate = 0.9;
            window.speechSynthesis.speak(speech);
        }}
        </script>
        """,
        height=45
    )


def describe_medicine(med):
    return (
        f'اسم الدواء: {med["name"]}. '
        f'نوع الدواء: {med["type"]}. '
        f'الجرعة المسجلة: {med["dose"]}. '
        f'الوقت: {med["time"]}، {med["period"]}. '
        f'تعليمات الطعام: {med["meal"]}. '
        f'ملاحظات: {med["notes"]}.'
    )


def time_minutes(med):
    try:
        hour, minute = map(int, med["time"].split(":"))
        return hour * 60 + minute
    except (ValueError, KeyError):
        return 9999


def next_medicine():
    if not st.session_state.medicines:
        return None

    now = datetime.now()
    current = now.hour * 60 + now.minute

    future = [
        med for med in st.session_state.medicines
        if time_minutes(med) >= current
    ]

    if future:
        return min(future, key=time_minutes)

    return min(st.session_state.medicines, key=time_minutes)


# ---------- رأس الصفحة ----------
st.markdown("""
<div class="hero">
    <h1>💙 مُجيب</h1>
    <p>المساعد الصحي الشخصي</p>
    <p>أدويتك ومواعيدك ومعلوماتك في مكان واحد.</p>
</div>
""", unsafe_allow_html=True)

next_med = next_medicine()

a, b, c = st.columns(3)

with a:
    st.markdown(f"""
    <div class="metric">
        <div>💊 الأدوية المسجلة</div>
        <h2>{len(st.session_state.medicines)}</h2>
        <div class="small">أدويتك التي أضفتِها</div>
    </div>
    """, unsafe_allow_html=True)

with b:
    st.markdown(f"""
    <div class="metric">
        <div>⏰ الموعد القادم</div>
        <h2>{next_med["time"] if next_med else "—"}</h2>
        <div class="small">حسب المواعيد المسجلة</div>
    </div>
    """, unsafe_allow_html=True)

with c:
    st.markdown(f"""
    <div class="metric">
        <div>⌚ الساعة الذكية</div>
        <h2 style="font-size:18px">
            {"تجريبية: متصلة" if st.session_state.watch_connected else "غير متصلة"}
        </h2>
        <div class="small">محاكاة للعرض</div>
    </div>
    """, unsafe_allow_html=True)

st.write("")

tabs = st.tabs([
    "🏠 الرئيسية",
    "💊 أدويتي",
    "➕ إضافة دواء",
    "🔊 الصوت",
    "⌚ الساعة",
    "💬 المساعد",
    "🆘 الطوارئ"
])


# ---------- الرئيسية ----------
with tabs[0]:
    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.subheader("أهلًا بك في مُجيب")
    st.write("من هنا تقدرين تتابعين الأدوية التي أدخلتِها بنفسك.")
    st.info("﴿وَإِذَا مَرِضْتُ فَهُوَ يَشْفِينِ﴾")
    st.markdown("</div>", unsafe_allow_html=True)

    if next_med:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("الدواء القادم في القائمة")
        st.markdown(
            f'<span style="display:inline-block;width:13px;height:13px;'
            f'border-radius:50%;background:{next_med["color"]};"></span> '
            f'**{next_med["name"]}**',
            unsafe_allow_html=True
        )
        st.write(f'الجرعة: {next_med["dose"]}')
        st.write(f'الوقت: {next_med["time"]}، {next_med["period"]}')

        if st.button("🔊 سماع معلومات الدواء", key="home_voice"):
            speak_arabic(describe_medicine(next_med))

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.subheader("💊 ابدئي بإضافة أول دواء")
        st.write("قائمة أدويتك فارغة حاليًا، وما أضفنا أي دواء من عندنا.")
        st.markdown("</div>", unsafe_allow_html=True)


# ---------- أدويتي ----------
with tabs[1]:
    st.subheader("💊 أدويتي")

    if not st.session_state.medicines:
        st.info("ما أضفتِ أي دواء حتى الآن. استخدمي قسم «إضافة دواء».")

    for i, med in enumerate(st.session_state.medicines):
        st.markdown('<div class="card">', unsafe_allow_html=True)

        st.markdown(
            f'<span style="display:inline-block;width:15px;height:15px;'
            f'border-radius:50%;background:{med["color"]};"></span> '
            f'**{med["name"]}**',
            unsafe_allow_html=True
        )
        st.write(f'**نوع الدواء:** {med["type"]}')
        st.write(f'**الجرعة:** {med["dose"]}')
        st.write(f'**الوقت:** {med["time"]}، {med["period"]}')
        st.write(f'**الطعام:** {med["meal"]}')

        if med["notes"]:
            st.write(f'**ملاحظات:** {med["notes"]}')

        if st.button("🔊 قراءة التفاصيل", key=f"read_{i}"):
            speak_arabic(describe_medicine(med))

        if st.button("🗑️ حذف هذا الدواء", key=f"remove_{i}"):
            st.session_state.medicines.pop(i)
            save_medicines()
            st.rerun()

        st.markdown("</div>", unsafe_allow_html=True)


# ---------- إضافة دواء ----------
with tabs[2]:
    st.subheader("➕ إضافة دواء جديد")
    st.write("عبّي الحقول حسب الوصفة أو تعليمات الصيدلي.")

    with st.form("add_medicine", clear_on_submit=True):
        name = st.text_input("اسم الدواء", placeholder="اكتبي اسم الدواء")

        med_type = st.selectbox(
            "نوع الدواء",
            ["حبوب", "كبسولات", "شراب", "قطرات", "كريم", "بخاخ", "نوع آخر"]
        )

        dose = st.text_input(
            "الجرعة",
            placeholder="اكتبي الجرعة المسجلة في الوصفة"
        )

        col1, col2 = st.columns(2)

        with col1:
            med_time = st.time_input(
                "الساعة والدقيقة",
                value=dt_time(8, 30),
                step=300
            )

        with col2:
            period = st.radio(
                "الفترة",
                ["صباحًا", "مساءً"],
                horizontal=True
            )

        meal = st.selectbox(
            "تعليمات الطعام",
            ["حسب الوصفة", "قبل الطعام", "بعد الطعام", "مع الطعام", "غير محدد"]
        )

        color = st.color_picker("لون الدواء", "#E74C3C")

        notes = st.text_area(
            "ملاحظات إضافية",
            placeholder="أي تعليمات أخرى من الوصفة"
        )

        submitted = st.form_submit_button(
            "💾 حفظ الدواء",
            use_container_width=True
        )

        if submitted:
            if not name.strip() or not dose.strip():
                st.error("اكتبي اسم الدواء والجرعة أولًا.")
            else:
                hour = med_time.hour

                if period == "مساءً" and hour < 12:
                    hour += 12
                elif period == "صباحًا" and hour == 12:
                    hour = 0

                st.session_state.medicines.append({
                    "name": name.strip(),
                    "type": med_type,
                    "dose": dose.strip(),
                    "time": f"{hour:02d}:{med_time.minute:02d}",
                    "period": period,
                    "meal": meal,
                    "notes": notes.strip(),
                    "color": color
                })

                save_medicines()
                st.success("انحفظ الدواء بنجاح 💙")
                st.rerun()


# ---------- الصوت ----------
with tabs[3]:
    st.subheader("🔊 التذكير الصوتي")

    if st.session_state.medicines:
        chosen = st.selectbox(
            "اختاري الدواء",
            range(len(st.session_state.medicines)),
            format_func=lambda i: st.session_state.medicines[i]["name"]
        )

        med = st.session_state.medicines[chosen]

        st.markdown('<div class="card">', unsafe_allow_html=True)
        st.write(f'**الاسم:** {med["name"]}')
        st.write(f'**الجرعة:** {med["dose"]}')
        st.write(f'**الموعد:** {med["time"]}، {med["period"]}')

        if st.button("▶️ تشغيل الصوت", use_container_width=True):
            speak_arabic(describe_medicine(med))

        st.markdown("</div>", unsafe_allow_html=True)
    else:
        st.info("أضيفي دواءً أولًا حتى تقدرين تسمعين تفاصيله.")

    st.warning(
        "الصوت يعمل عند الضغط على الزر فقط. هذه النسخة لا ترسل تنبيهًا تلقائيًا "
        "بعد إغلاق التطبيق."
    )


# ---------- الساعة ----------
with tabs[4]:
    st.subheader("⌚ الساعة الذكية")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("🔋 البطارية التجريبية: 95%")
    st.write(
        "حالة الاتصال: "
        + ("متصلة تجريبيًا" if st.session_state.watch_connected else "غير متصلة")
    )
    st.caption("لا يوجد اتصال فعلي بساعة ذكية.")

    if st.button(
        "قطع الاتصال التجريبي"
        if st.session_state.watch_connected
        else "تفعيل الاتصال التجريبي"
    ):
        st.session_state.watch_connected = not st.session_state.watch_connected
        st.rerun()

    st.markdown("</div>", unsafe_allow_html=True)


# ---------- المساعد النصي ----------
with tabs[5]:
    st.subheader("💬 المساعد الصحي")
    st.caption("ردود تجريبية محدودة وليست تشخيصًا طبيًا.")

    for message in st.session_state.chat:
        with st.chat_message(message["role"]):
            st.write(message["content"])

    prompt = st.chat_input("اكتبي سؤالك هنا...")

    if prompt:
        st.session_state.chat.append({
            "role": "user",
            "content": prompt
        })

        lower = prompt.lower()

        if any(word in lower for word in ["دواء", "جرعة", "الأدوية"]):
            reply = (
                "راجعي البيانات المسجلة في قسم «أدويتي»، "
                "واتبعي الوصفة الطبية. اسألي الطبيب أو الصيدلي عند الشك."
            )
        elif any(word in lower for word in ["موعد", "وقت", "متى"]):
            if next_med:
                reply = (
                    f'الوقت المسجل للدواء {next_med["name"]} هو '
                    f'{next_med["time"]}، {next_med["period"]}.'
                )
            else:
                reply = "قائمة الأدوية فارغة حاليًا."
        elif any(word in lower for word in ["طوارئ", "إسعاف", "خطر"]):
            reply = (
                "إذا كانت الحالة طارئة، اطلبي المساعدة مباشرة من خدمات الطوارئ المحلية. "
                "هذا التطبيق لا يجري مكالمات."
            )
        else:
            reply = (
                "أقدر أساعدك في فهم أقسام التطبيق والبيانات المسجلة. "
                "للتشخيص أو تغيير الجرعات، راجعي الطبيب أو الصيدلي."
            )

        st.session_state.chat.append({
            "role": "assistant",
            "content": reply
        })
        st.rerun()


# ---------- الطوارئ ----------
with tabs[6]:
    st.subheader("🆘 الطوارئ")

    st.markdown('<div class="card">', unsafe_allow_html=True)
    st.write("قسم تجريبي لتوضيح واجهة الطوارئ.")
    st.text_input("رمز تعريفي تجريبي (اختياري)")
    st.info("لا توجد مكالمات حقيقية أو مشاركة موقع أو إرسال تنبيهات.")

    if st.button("عرض رسالة الطوارئ"):
        st.warning(
            "هذه رسالة تجريبية فقط. عند وجود خطر حقيقي، "
            "تواصلي مع خدمات الطوارئ المحلية مباشرة."
        )

    st.markdown("</div>", unsafe_allow_html=True)


st.divider()
st.caption(
    "مُجيب 💙 | نموذج تعليمي. البيانات محفوظة في ملف محلي على هذا الجهاز. "
    "لا يُعد التطبيق بديلًا عن الطبيب أو الصيدلي."
)

