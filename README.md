# 배민 DSM 영업 마스터북 — Streamlit 앱 (코드만 공개)

- 이 저장소: 앱 코드만. 마스터북 내용(HTML)은 **비공개 저장소 jhseo-svg/dsm-masterbook-v7** 의 `masterbook.html`
- 앱은 Secrets의 읽기 전용 토큰으로 비공개 저장소에서 HTML을 가져와 보여줌 (5분 캐시, 사이드바 '콘텐츠 새로고침')
- 내용 갱신: masterbook-v7에서 build → `cp index.html ../dsm-masterbook-v7/masterbook.html` → push (앱 코드는 손댈 필요 없음)
- 로그인: Secrets에 [auth] 추가 시 Google 로그인 게이트 자동 활성 (secrets.toml.example 참고)

## Secrets 설정 (1회)
1. GitHub → Settings → Developer settings → Personal access tokens → **Fine-grained tokens** → Generate
   - Repository access: Only select repositories → `dsm-masterbook-v7`
   - Permissions → Repository permissions → **Contents: Read-only**
2. Streamlit Cloud → 이 앱 → Settings → Secrets:
   ```toml
   [content]
   github_token = "github_pat_..."
   ```
