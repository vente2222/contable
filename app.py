# app.py - النسخة النهائية مع التعديلات المطلوبة
import streamlit as st
from supabase import create_client, Client
from datetime import datetime
import pandas as pd

# معلومات Supabase
SUPABASE_URL = "https://keubmdkdgahnjzrdczjo.supabase.co"
SUPABASE_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6ImtldWJtZGtkZ2Fobmp6cmRjempvIiwicm9sZSI6ImFub24iLCJpYXQiOjE3Nzg5NTEyOTQsImV4cCI6MjA5NDUyNzI5NH0.SBBZexIt5TBOno93WHm_LdDTEpKLXGN78kllqSIHETs"

# تهيئة اتصال Supabase
@st.cache_resource
def init_supabase():
    return create_client(SUPABASE_URL, SUPABASE_KEY)

supabase = init_supabase()

# قاموس الترجمة
translations = {
    "ar": {
        "app_title": "Attijariwafa contaple",
        "login_title": "تسجيل الدخول",
        "username": "اسم المستخدم",
        "password": "كلمة المرور",
        "login_btn": "دخول",
        "logout_btn": "تسجيل خروج",
        "error_credentials": "اسم المستخدم أو كلمة المرور غير صحيحة",
        "welcome": "مرحباً",
        "balance": "الرصيد المتبقي",
        "history": "أخر العمليات",
        "no_transactions": "لا توجد عمليات مسجلة",
        "reason": "البيان",
        "amount": "المبلغ",
        "datetime": "التاريخ",
        "menu": "القائمة",
        "recharge_system": "تعبئة رصيد",
        "create_account": "إنشاء حساب",
        "pay_bill": "تأدية فاتورة",
        "quick_recharge": "تعبئة سريعة",
        "other": "عملية أخرى",
        "save_btn": "تأكيد",
        "success": "تمت العملية بنجاح",
        "phone_number": "رقم الهاتف",
        "bill_number": "رقم الفاتورة",
        "offer": "العرض",
        "amount_placeholder": "أدخل المبلغ",
        "reason_placeholder": "سبب العملية",
        "name": "الإسم",
        "surname": "النسب",
        "login": "اسم المستخدم",
        "password_field": "كلمة المرور",
        "user_exists": "هذا الاسم المستخدم موجود بالفعل",
        "select_user": "صاحب الفاتورة",
        "connection_error": "خطأ في الاتصال",
        "dashboard": "الرئيسية",
        "phone_required": "رقم الهاتف مطلوب",
        "all_transactions": "جميع العمليات",
    },
    "fr": {
        "app_title": "Attijariwafa contaple",
        "login_title": "Connexion",
        "username": "Nom d'utilisateur",
        "password": "Mot de passe",
        "login_btn": "Se connecter",
        "logout_btn": "Déconnexion",
        "error_credentials": "Nom d'utilisateur ou mot de passe incorrect",
        "welcome": "Bonjour",
        "balance": "Solde restant",
        "history": "Dernières opérations",
        "no_transactions": "Aucune transaction enregistrée",
        "reason": "Libellé",
        "amount": "Montant",
        "datetime": "Date",
        "menu": "Menu",
        "recharge_system": "Recharger",
        "create_account": "Créer compte",
        "pay_bill": "Payer facture",
        "quick_recharge": "Recharge rapide",
        "other": "Autre",
        "save_btn": "Confirmer",
        "success": "Opération réussie",
        "phone_number": "Numéro de téléphone",
        "bill_number": "Numéro de facture",
        "offer": "Offre",
        "amount_placeholder": "Entrez le montant",
        "reason_placeholder": "Raison de l'opération",
        "name": "Prénom",
        "surname": "Nom",
        "login": "Nom d'utilisateur",
        "password_field": "Mot de passe",
        "user_exists": "Ce nom d'utilisateur existe déjà",
        "select_user": "Propriétaire de la facture",
        "connection_error": "Erreur de connexion",
        "dashboard": "Tableau de bord",
        "phone_required": "Le numéro de téléphone est requis",
        "all_transactions": "Toutes les opérations",
    }
}

# إدارة اللغة
def init_language():
    if "language" not in st.session_state:
        st.session_state["language"] = "ar"
    return translations[st.session_state["language"]]

# حساب الرصيد الحقيقي للنظام
def get_system_balance():
    try:
        all_recharges = supabase.table("transactions").select("*").eq("type", "recharge").execute()
        total_recharges = sum([t['amount'] for t in all_recharges.data]) if all_recharges.data else 0
        
        all_payments = supabase.table("transactions").select("*").eq("type", "payment").execute()
        total_payments = sum([t['amount'] for t in all_payments.data]) if all_payments.data else 0
        
        return total_recharges - total_payments
    except:
        return 0

# تحديث رصيد المستخدم (يتم حسابه من العمليات مباشرة)
def get_user_balance(user_id):
    try:
        payments = supabase.table("transactions").select("*").eq("user_id", user_id).eq("type", "payment").execute()
        total_payments = sum([t['amount'] for t in payments.data]) if payments.data else 0
        
        recharges = supabase.table("transactions").select("*").eq("user_id", user_id).eq("type", "recharge").execute()
        total_recharges = sum([r['amount'] for r in recharges.data]) if recharges.data else 0
        
        return total_recharges - total_payments
    except:
        return 0

# دالة تسجيل الدخول - تصميم أنيق بدون مربعات
def login(t):
    st.markdown("""
    <style>
    /* خلفية الصفحة */
    .stApp {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    }
    
    /* إخفاء العناصر الافتراضية */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}
    
    /* تنسيق الحقول */
    .stTextInput > div > div > input {
        background: rgba(255,255,255,0.95);
        border: none;
        border-radius: 12px;
        padding: 14px 20px;
        font-size: 16px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
        transition: all 0.3s;
    }
    
    .stTextInput > div > div > input:focus {
        box-shadow: 0 4px 20px rgba(0,0,0,0.15);
        transform: translateY(-2px);
    }
    
    /* تنسيق زر تسجيل الدخول */
    .stButton > button {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        color: white;
        border: none;
        border-radius: 12px;
        padding: 14px;
        font-size: 18px;
        font-weight: bold;
        transition: all 0.3s;
        box-shadow: 0 4px 15px rgba(0,0,0,0.2);
    }
    
    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 20px rgba(0,0,0,0.25);
    }
    
    /* تنسيق زر اللغة */
    .stButton > button:has(🌐) {
        background: rgba(255,255,255,0.2);
        backdrop-filter: blur(10px);
    }
    </style>
    """, unsafe_allow_html=True)
    
    # وسط الصفحة
    col1, col2, col3 = st.columns([1, 2, 1])
    with col2:
        st.markdown('<div style="text-align: center; padding: 60px 40px;">', unsafe_allow_html=True)
        
        # الشعار
        st.markdown("""
        <div style="margin-bottom: 50px;">
            <h1 style="color: white; font-size: 48px; margin-bottom: 10px;">🏦</h1>
            <h1 style="color: white; font-size: 32px; font-weight: 300;">Attijariwafa</h1>
            <h2 style="color: rgba(255,255,255,0.9); font-size: 24px;">contaple</h2>
        </div>
        """, unsafe_allow_html=True)
        
        # نموذج تسجيل الدخول
        with st.form("login_form"):
            username = st.text_input(t["username"], placeholder="exemple@domaine.com", label_visibility="collapsed")
            password = st.text_input(t["password"], type="password", placeholder="••••••••", label_visibility="collapsed")
            
            st.markdown("<div style='height: 20px;'></div>", unsafe_allow_html=True)
            
            submitted = st.form_submit_button(t["login_btn"], use_container_width=True)
            
            if submitted:
                try:
                    response = supabase.table("users").select("*").eq("login", username).eq("password", password).execute()
                    
                    if response.data:
                        user = response.data[0]
                        st.session_state["logged_in"] = True
                        st.session_state["user"] = user
                        st.session_state["current_page"] = "dashboard"
                        st.rerun()
                    else:
                        st.error(t["error_credentials"])
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")
        
        # زر تبديل اللغة
        if st.button("🌐 " + ("Français" if st.session_state["language"] == "ar" else "العربية"), use_container_width=True):
            st.session_state["language"] = "fr" if st.session_state["language"] == "ar" else "ar"
            st.rerun()
        
        st.markdown('</div>', unsafe_allow_html=True)

# شريط علوي احترافي بدون بحث
def top_bar(t):
    user = st.session_state["user"]
    
    st.markdown(f"""
    <style>
    .top-bar {{
        background-color: #1a1a2e;
        padding: 16px 32px;
        margin-bottom: 30px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    }}
    .logo {{
        color: white;
        font-size: 20px;
        font-weight: bold;
        letter-spacing: 1px;
    }}
    .logo span {{
        color: #ff6b35;
    }}
    .user-info {{
        color: white;
        font-size: 14px;
        background: rgba(255,255,255,0.1);
        padding: 8px 16px;
        border-radius: 20px;
    }}
    </style>
    
    <div class="top-bar">
        <div class="logo">Attijariwafa<span> contaple</span></div>
        <div class="user-info">
            👤 {user['name']} {user['surname']}
        </div>
    </div>
    """, unsafe_allow_html=True)

# عرض سجل العمليات بشكل أنيق في المنتصف
def show_history_like_bank(t):
    user = st.session_state["user"]
    
    st.markdown("""
    <style>
    .history-container {
        max-width: 800px;
        margin: 0 auto;
    }
    .history-card {
        background: white;
        border-radius: 16px;
        margin-bottom: 12px;
        padding: 16px 20px;
        border-left: 4px solid;
        transition: all 0.2s;
        cursor: pointer;
        box-shadow: 0 2px 8px rgba(0,0,0,0.05);
    }
    .history-card:hover {
        background: #f8f9fa;
        transform: translateX(4px);
        box-shadow: 0 4px 12px rgba(0,0,0,0.1);
    }
    .history-date {
        font-size: 12px;
        color: #6c757d;
        margin-bottom: 6px;
    }
    .history-reason {
        font-size: 14px;
        font-weight: 500;
        color: #212529;
        margin-bottom: 6px;
    }
    .history-amount {
        font-size: 16px;
        font-weight: bold;
        text-align: right;
        margin-top: -30px;
    }
    .amount-positive {
        color: #28a745;
    }
    .amount-negative {
        color: #dc3545;
    }
    .history-phone {
        font-size: 11px;
        color: #6c757d;
        margin-top: 8px;
        padding-top: 6px;
        border-top: 1px solid #e9ecef;
    }
    .section-title {
        font-size: 20px;
        font-weight: 600;
        color: #1a1a2e;
        margin-bottom: 20px;
        padding-bottom: 10px;
        border-bottom: 2px solid #e0e0e0;
        text-align: center;
    }
    </style>
    """, unsafe_allow_html=True)
    
    st.markdown(f'<div class="section-title">📋 {t["history"]}</div>', unsafe_allow_html=True)
    st.markdown('<div class="history-container">', unsafe_allow_html=True)
    
    try:
        response = supabase.table("transactions").select("*").eq("user_id", user['id']).order("created_at", desc=True).limit(20).execute()
        
        if response.data:
            for trans in response.data:
                trans_date = datetime.fromisoformat(trans['created_at'].replace('Z', '+00:00'))
                formatted_date = trans_date.strftime('%d/%m/%Y %H:%M')
                
                is_positive = trans['type'] == 'recharge'
                amount_color = "amount-positive" if is_positive else "amount-negative"
                amount_sign = "+" if is_positive else "-"
                border_color = "#28a745" if is_positive else "#dc3545"
                
                st.markdown(f"""
                <div class="history-card" style="border-left-color: {border_color};">
                    <div class="history-date">{formatted_date}</div>
                    <div class="history-reason">{trans['reason'][:60]}</div>
                    <div class="history-amount {amount_color}">{amount_sign} {trans['amount']:,.2f} DH</div>
                    <div class="history-phone">📱 {trans.get('phone_number', 'Non renseigné')}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            st.info(t['no_transactions'])
    except Exception as e:
        st.error(f"{t['connection_error']}: {str(e)}")
    
    st.markdown('</div>', unsafe_allow_html=True)

# صفحة تعبئة رصيد النظام
def page_recharge_system(t):
    st.markdown(f"## 💳 {t['recharge_system']}")
    
    with st.form("recharge_form"):
        amount = st.number_input(t["amount"], min_value=0.0, step=100.0, placeholder=t["amount_placeholder"])
        reason = st.text_input(t["reason"], placeholder=t["reason_placeholder"])
        phone_number = st.text_input(t["phone_number"], placeholder="05XXXXXXXX")
        submitted = st.form_submit_button(t["save_btn"], use_container_width=True)
        
        if submitted and amount > 0 and reason:
            if not phone_number:
                st.warning(t["phone_required"])
            else:
                try:
                    data = {
                        "user_id": st.session_state["user"]["id"],
                        "amount": amount,
                        "reason": f"{reason} - Tél: {phone_number}",
                        "type": "recharge",
                        "phone_number": phone_number,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table("transactions").insert(data).execute()
                    st.success(t["success"])
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")

# صفحة إنشاء حساب
def page_create_account(t):
    st.markdown(f"## 👤 {t['create_account']}")
    
    with st.form("create_user_form"):
        name = st.text_input(t["name"])
        surname = st.text_input(t["surname"])
        login = st.text_input(t["login"])
        password = st.text_input(t["password_field"], type="password")
        phone = st.text_input(t["phone_number"], placeholder="05XXXXXXXX")
        submitted = st.form_submit_button(t["save_btn"], use_container_width=True)
        
        if submitted and all([name, surname, login, password]):
            if not phone:
                st.warning(t["phone_required"])
            else:
                try:
                    check = supabase.table("users").select("*").eq("login", login).execute()
                    if check.data:
                        st.error(t["user_exists"])
                    else:
                        data = {
                            "name": name,
                            "surname": surname,
                            "login": login,
                            "password": password,
                            "phone": phone
                        }
                        supabase.table("users").insert(data).execute()
                        st.success(t["success"])
                        st.balloons()
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")

# صفحة تأدية فاتورة
def page_pay_bill(t):
    st.markdown(f"## 🧾 {t['pay_bill']}")
    
    try:
        users = supabase.table("users").select("*").execute()
        users_list = {f"{u['name']} {u['surname']}": u['id'] for u in users.data}
    except:
        users_list = {}
    
    with st.form("bill_form"):
        amount = st.number_input(t["amount"], min_value=0.0, step=100.0, placeholder=t["amount_placeholder"])
        reason = st.text_input(t["reason"], placeholder=t["reason_placeholder"])
        bill_number = st.text_input(t["bill_number"], placeholder="Facture-XXXX")
        phone_number = st.text_input(t["phone_number"], placeholder="05XXXXXXXX")
        user_name = st.selectbox(t["select_user"], list(users_list.keys()))
        submitted = st.form_submit_button(t["save_btn"], use_container_width=True)
        
        if submitted and amount > 0 and reason and user_name:
            if not phone_number:
                st.warning(t["phone_required"])
            else:
                try:
                    full_reason = f"{reason} - Facture: {bill_number} - Tél: {phone_number}" if bill_number else f"{reason} - Tél: {phone_number}"
                    data = {
                        "user_id": users_list[user_name],
                        "amount": amount,
                        "reason": full_reason,
                        "type": "payment",
                        "phone_number": phone_number,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table("transactions").insert(data).execute()
                    st.success(t["success"])
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")

# صفحة تعبئة سريعة
def page_quick_recharge(t):
    st.markdown(f"## ⚡ {t['quick_recharge']}")
    
    with st.form("quick_recharge_form"):
        amount = st.number_input(t["amount"], min_value=0.0, step=100.0, placeholder=t["amount_placeholder"])
        offer = st.text_input(t["offer"], placeholder="مثال: 20% بونص")
        phone_number = st.text_input(t["phone_number"], placeholder="05XXXXXXXX")
        submitted = st.form_submit_button(t["save_btn"], use_container_width=True)
        
        if submitted and amount > 0:
            if not phone_number:
                st.warning(t["phone_required"])
            else:
                try:
                    full_reason = f"Recharge rapide - {offer} - Tél: {phone_number}" if offer else f"Recharge rapide - Tél: {phone_number}"
                    data = {
                        "user_id": st.session_state["user"]["id"],
                        "amount": amount,
                        "reason": full_reason,
                        "type": "recharge",
                        "phone_number": phone_number,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table("transactions").insert(data).execute()
                    st.success(t["success"])
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")

# صفحة عمليات أخرى
def page_other(t):
    st.markdown(f"## 🔄 {t['other']}")
    
    with st.form("other_form"):
        amount = st.number_input(t["amount"], min_value=0.0, step=100.0, placeholder=t["amount_placeholder"])
        reason = st.text_input(t["reason"], placeholder=t["reason_placeholder"])
        phone_number = st.text_input(t["phone_number"], placeholder="05XXXXXXXX")
        trans_type = st.selectbox("نوع العملية", ["سحب (Débit)", "إيداع (Crédit)"])
        submitted = st.form_submit_button(t["save_btn"], use_container_width=True)
        
        if submitted and amount > 0 and reason:
            if not phone_number:
                st.warning(t["phone_required"])
            else:
                try:
                    full_reason = f"{reason} - Tél: {phone_number}"
                    data = {
                        "user_id": st.session_state["user"]["id"],
                        "amount": amount,
                        "reason": full_reason,
                        "type": "payment" if "سحب" in trans_type else "recharge",
                        "phone_number": phone_number,
                        "created_at": datetime.now().isoformat()
                    }
                    supabase.table("transactions").insert(data).execute()
                    st.success(t["success"])
                    st.balloons()
                    st.rerun()
                except Exception as e:
                    st.error(f"{t['connection_error']}: {str(e)}")

# عرض الرصيد المتبقي في المنتصف
def show_balance_card(t, user_balance):
    st.markdown(f"""
    <style>
    .balance-container {{
        max-width: 800px;
        margin: 0 auto 30px auto;
    }}
    .balance-card {{
        background: linear-gradient(135deg, #1a3e6f 0%, #0f2b4f 100%);
        border-radius: 24px;
        padding: 32px;
        text-align: center;
        box-shadow: 0 10px 30px rgba(0,0,0,0.15);
    }}
    .balance-label {{
        color: rgba(255,255,255,0.8);
        font-size: 16px;
        letter-spacing: 2px;
        margin-bottom: 12px;
        text-transform: uppercase;
    }}
    .balance-amount {{
        color: white;
        font-size: 48px;
        font-weight: bold;
    }}
    .balance-currency {{
        color: rgba(255,255,255,0.8);
        font-size: 20px;
        margin-left: 8px;
    }}
    </style>
    
    <div class="balance-container">
        <div class="balance-card">
            <div class="balance-label">{t['balance']}</div>
            <div class="balance-amount">{user_balance:,.2f}<span class="balance-currency">DH</span></div>
        </div>
    </div>
    """, unsafe_allow_html=True)

# الصفحة الرئيسية (Dashboard)
def dashboard(t):
    user = st.session_state["user"]
    user_balance = get_user_balance(user['id'])
    
    # عرض الرصيد في المنتصف
    show_balance_card(t, user_balance)
    
    # عرض سجل العمليات في المنتصف
    show_history_like_bank(t)

# عرض الشريط الجانبي مع الأزرار
def sidebar_menu(t):
    is_admin = st.session_state["user"]['login'] == "yassinederra@admin"
    
    with st.sidebar:
        st.markdown("""
        <style>
        section[data-testid="stSidebar"] {
            background-color: #1a1a2e;
        }
        section[data-testid="stSidebar"] * {
            color: white !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        st.markdown("### MAIN NAVIGATION")
        st.markdown("---")
        
        if st.button(f"📊 {t['dashboard']}", use_container_width=True):
            st.session_state["current_page"] = "dashboard"
            st.rerun()
        
        if is_admin:
            st.markdown("### Gestion")
            st.markdown("---")
            
            buttons = [
                {"icon": "💰", "title": t['recharge_system'], "page": "recharge"},
                {"icon": "👤", "title": t['create_account'], "page": "create"},
                {"icon": "📄", "title": t['pay_bill'], "page": "bill"},
                {"icon": "⚡", "title": t['quick_recharge'], "page": "quick"},
                {"icon": "🔄", "title": t['other'], "page": "other"}
            ]
            
            for btn in buttons:
                if st.button(f"{btn['icon']} {btn['title']}", use_container_width=True):
                    st.session_state["current_page"] = btn['page']
                    st.rerun()
        
        st.markdown("---")
        if st.button(f"🌐 {'Français' if st.session_state['language'] == 'ar' else 'العربية'}", use_container_width=True):
            st.session_state["language"] = "fr" if st.session_state["language"] == "ar" else "ar"
            st.rerun()
        
        if st.button(f"🚪 {t['logout_btn']}", use_container_width=True):
            for key in ["logged_in", "user", "current_page"]:
                if key in st.session_state:
                    del st.session_state[key]
            st.rerun()

# الواجهة الرئيسية
def main():
    st.set_page_config(
        page_title="Attijariwafa contaple",
        page_icon="🏦",
        layout="wide",
        initial_sidebar_state="expanded"
    )
    
    t = init_language()
    
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "dashboard"
    
    # CSS عام
    st.markdown("""
    <style>
    .stApp {
        background-color: #f5f7fa;
    }
    
    .stTextInput > div > div > input, .stNumberInput > div > div > input, .stTextArea > div > div > textarea, .stSelectbox > div > div > select {
        border-radius: 12px;
        border: 1px solid #e0e0e0;
        padding: 12px;
    }
    
    .stButton > button {
        background-color: #1a3e6f;
        color: white;
        border: none;
        border-radius: 12px;
        padding: 12px;
        transition: all 0.2s;
    }
    
    .stButton > button:hover {
        background-color: #0f2b4f;
        transform: translateY(-2px);
    }
    
    div[data-testid="stForm"] {
        background: white;
        padding: 24px;
        border-radius: 20px;
        box-shadow: 0 2px 10px rgba(0,0,0,0.05);
    }
    
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    </style>
    """, unsafe_allow_html=True)
    
    if not st.session_state["logged_in"]:
        login(t)
    else:
        top_bar(t)
        
        col_sidebar, col_main = st.columns([0.25, 0.75])
        
        with col_sidebar:
            sidebar_menu(t)
        
        with col_main:
            if st.session_state["current_page"] == "dashboard":
                dashboard(t)
            elif st.session_state["current_page"] == "recharge":
                page_recharge_system(t)
            elif st.session_state["current_page"] == "create":
                page_create_account(t)
            elif st.session_state["current_page"] == "bill":
                page_pay_bill(t)
            elif st.session_state["current_page"] == "quick":
                page_quick_recharge(t)
            elif st.session_state["current_page"] == "other":
                page_other(t)

if __name__ == "__main__":
    main()