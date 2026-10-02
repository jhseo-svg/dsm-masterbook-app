"""
배민 DSM 영업 마스터북 — 공개 코드 / 비공개 콘텐츠 구조

- 이 저장소(공개)에는 코드만 있고, 마스터북 HTML은 비공개 저장소(jhseo-svg/dsm-masterbook-v7)에 있음
- 앱이 켜질 때 Secrets의 읽기 전용 토큰으로 비공개 저장소에서 HTML을 가져와 임베드 (5분 캐시)
- 로그인 게이트: Secrets에 [auth]/[auth.google]이 있으면 Google 로그인 필수, 없으면 링크 열람
"""
import os
from urllib.request import Request, urlopen
from urllib.error import HTTPError, URLError

import streamlit as st
import streamlit.components.v1 as components

st.set_page_config(page_title="배민 DSM 영업 마스터북", page_icon="📗",
                   layout="wide", initial_sidebar_state="collapsed")

CONTENT_REPO = "jhseo-svg/dsm-masterbook-v7"
CONTENT_PATH = "masterbook.html"
CONTENT_REF = "main"


def _secrets():
    try:
        return st.secrets.to_dict()
    except Exception:
        return {}


SEC = _secrets()
HAS_AUTH = "auth" in SEC and "google" in SEC["auth"]
DEV = os.environ.get("MB_DEV") == "1"


# ---------- 로그인 게이트 (Secrets [auth]가 있을 때만) ----------
def gate() -> str:
    if not HAS_AUTH:
        return "open"
    if not st.user.is_logged_in:
        st.markdown("""
        <style>[data-testid="stSidebar"],[data-testid="stHeader"],footer{display:none}
        .lw{max-width:420px;margin:12vh auto 0;text-align:center}.lw h1{font-size:26px;font-weight:800;margin:0 0 6px}
        .lw p{color:#6b7280;font-size:15px;margin:0 0 22px}
        .conf{display:inline-block;font-size:12px;font-weight:700;color:#B45309;background:#FEF3C7;border-radius:6px;padding:2px 8px;margin-bottom:14px}</style>
        <div class="lw"><div class="conf">대외비</div><h1>배민 DSM 영업 마스터북</h1><p>Google 계정으로 로그인하면 열람할 수 있습니다.</p></div>
        """, unsafe_allow_html=True)
        _, c, _ = st.columns([1, 1.2, 1])
        with c:
            st.button("Google 계정으로 로그인", on_click=st.login, args=("google",), type="primary", use_container_width=True)
        st.stop()
    email = str(st.user.get("email", "")).strip().lower()
    acc = SEC.get("access", {})
    domains = [d.lower() for d in acc.get("allowed_domains", ["woowahan.com"])]
    emails = [e.lower() for e in acc.get("allowed_emails", [])]
    if email.split("@")[-1] not in domains and email not in emails:
        st.error(f"접근 권한이 없는 계정입니다 — {email}")
        st.button("다른 계정으로 로그인", on_click=st.logout, type="primary")
        st.stop()
    return email


# ---------- 비공개 저장소에서 콘텐츠 가져오기 ----------
def _token() -> str:
    return (SEC.get("content", {}).get("github_token")
            or os.environ.get("MB_GITHUB_TOKEN") or "")


@st.cache_data(ttl=300, show_spinner="마스터북을 불러오는 중…")
def load_html(token: str) -> str:
    url = f"https://api.github.com/repos/{CONTENT_REPO}/contents/{CONTENT_PATH}?ref={CONTENT_REF}"
    req = Request(url, headers={"Authorization": f"Bearer {token}",
                                "Accept": "application/vnd.github.raw+json",
                                "User-Agent": "dsm-masterbook-app"})
    with urlopen(req, timeout=20) as r:
        return r.read().decode("utf-8")


email = gate()
token = _token()
if not token:
    st.error("콘텐츠 토큰이 없습니다. Streamlit Cloud → Settings → Secrets 에 아래를 넣어주세요.\n\n"
             "```toml\n[content]\ngithub_token = \"<dsm-masterbook-v7 읽기 전용 토큰>\"\n```")
    st.stop()
try:
    html = load_html(token)
except HTTPError as e:
    st.error(f"콘텐츠를 가져오지 못했습니다 (GitHub {e.code}). 토큰 권한(Contents: Read-only)과 저장소 이름을 확인해주세요.")
    st.stop()
except URLError as e:
    st.error(f"네트워크 오류: {e.reason}")
    st.stop()

with st.sidebar:
    st.caption("공개 모드 — Google 로그인 미설정" if email == "open" else f"로그인 계정: {email}")
    if email != "open":
        st.button("로그아웃", on_click=st.logout)
    if st.button("콘텐츠 새로고침"):
        load_html.clear(); st.rerun()

st.markdown("""
<style>
  #MainMenu, header, footer {visibility:hidden;}
  [data-testid="stHeader"], [data-testid="stDecoration"] {display:none;}
  .block-container {padding:0 !important; max-width:100% !important;}
  [data-testid="stAppViewContainer"] > .main {padding:0 !important;}
  [data-testid="stAppViewContainer"] iframe {height:100vh !important; width:100% !important; display:block; border:0;}
</style>
""", unsafe_allow_html=True)

html += ("\n<script>try{var fe=window.frameElement;if(fe){fe.style.height='100vh';fe.style.width='100%';fe.style.border='0';}}catch(e){}</script>"
         "\n<script>(function(){function h(){try{var tw=window.top,td=tw.document;if(!td.getElementById('mb-hide')){var s=td.createElement('style');s.id='mb-hide';"
         "s.textContent='[data-testid=\"manage-app-button\"],[data-testid=\"appCreatorAvatar\"],[class*=\"viewerBadge\"],[class*=\"profileBadge\"],[class*=\"creatorBadge\"]{display:none !important}';"
         "(td.head||td.documentElement).appendChild(s);}}catch(e){}}[400,1500,4000,10000].forEach(function(t){setTimeout(h,t)});})();</script>")
components.html(html, height=1000, scrolling=True)
