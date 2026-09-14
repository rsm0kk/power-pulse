# -*- coding: utf-8 -*-
"""
Power Equipment Pulse — 전력기기 대시보드 빌더
관세청 + DART + FRED 를 긁어서, 데이터가 통째로 박힌 단일 HTML 을 찍어낸다.

  실행:  python power_pulse.py
  미리보기(키 없이 화면만 확인):  python power_pulse.py --demo

산출물:  out/전력기기_대시보드_YYYYMMDD.html   ← 이 파일만 공유하면 됨
         store.json                          ← 과거 데이터 누적 보관(지우지 말 것)

API 키는 이 파일 안에만 있고 HTML 에는 들어가지 않는다. 이 .py 는 공유하지 말 것.
"""

import os, sys, json, time, io, re, zipfile, ssl, datetime as dt
import xml.etree.ElementTree as ET
import urllib.request, urllib.parse, urllib.error

# Windows 콘솔이 cp949 라서 em-dash(—) 등에서 죽는 문제 방지
for _s in (sys.stdout, sys.stderr):
    try:
        _s.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

# 백신·기업 프록시의 SSL 검사(중간자)로 인증서 검증이 깨지는 환경 대응:
# 먼저 정상 검증을 시도하고, 검증 실패가 나면 그때만 검증 없이 재시도한다.
_SSL_CTX = ssl.create_default_context()
_SSL_INSECURE = False

# ============================================================
# 1. 설정
# ============================================================
# API 키는 코드에 넣지 않는다(공개 저장소 유출 방지).
#  - GitHub Actions: 환경변수(Secrets)에서 읽음
#  - 로컬 실행: 같은 폴더의 secrets.json 에서 읽음 (git에 올리지 않음)
def _load_key(name):
    v = os.environ.get(name)
    if v:
        return v.strip()
    try:
        sp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "secrets.json")
        if os.path.exists(sp):
            return (json.load(open(sp, encoding="utf-8")).get(name) or "").strip()
    except Exception:
        pass
    return ""


CUSTOMS_KEY = _load_key("CUSTOMS_KEY")
DART_KEY    = _load_key("DART_KEY")
FRED_KEY    = _load_key("FRED_KEY")

MONTHS_BACK = 37          # 관세청 조회 기간(개월). YoY 비교하려면 25 이상 권장
QUARTERS_BACK = 9         # DART 분기 실적 조회 분기 수
ORDER_START_YEAR = 2023   # 수주잔고·신규수주 시계열 시작 연도
FILING_DAYS = 120         # 공시 조회 기간(일)
BASE_FX = 1380            # 시나리오 슬라이더 기본 환율

# ---- 관세청: HS 4단위로 조회하면 6단위 세부코드가 전부 딸려온다 (호출 최소화) ----
HS_PREFIXES = ["8504", "8535", "8537", "8544"]

# 6단위 코드 → (품목, 세부규격, 그룹).  여기 없는 코드는 버린다.
HS_MAP = {
    "850421": ("변압기", "유입식 650kVA 이하", "변압기"),
    "850422": ("변압기", "유입식 650kVA~10,000kVA", "변압기"),
    "850423": ("변압기", "유입식 10,000kVA 초과 (대형)", "변압기"),
    "850431": ("변압기", "기타 1kVA 이하", "변압기"),
    "850432": ("변압기", "기타 1~16kVA", "변압기"),
    "850433": ("변압기", "기타 16~500kVA", "변압기"),
    "850434": ("변압기", "기타 500kVA 초과", "변압기"),
    "850440": ("전력변환", "정지형 변환기 (PCS·인버터)", "전력변환"),
    "850450": ("전력변환", "기타 인덕터", "전력변환"),
    "853521": ("차단기·개폐기", "자동차단기 72.5kV 미만", "차단기·개폐기"),
    "853529": ("차단기·개폐기", "자동차단기 72.5kV 이상", "차단기·개폐기"),
    "853530": ("차단기·개폐기", "단로기·개폐기", "차단기·개폐기"),
    "853590": ("차단기·개폐기", "기타 고압 개폐기기", "차단기·개폐기"),
    "853710": ("배전반", "1,000V 이하 배전반·제어반", "배전반"),
    "853720": ("배전반", "1,000V 초과 배전반", "배전반"),
    "854442": ("전선·케이블", "커넥터 부착 1,000V 이하", "전선·케이블"),
    "854449": ("전선·케이블", "기타 절연전선 1,000V 이하", "전선·케이블"),
    "854460": ("전선·케이블", "1,000V 초과 절연전선", "전선·케이블"),
    "854470": ("전선·케이블", "광섬유 케이블", "전선·케이블"),
}
CNTY_TARGETS = [("US", "미국"), ("", "전체")]

# ---- DART: 커버리지 7사 (이름으로 corp_code 자동 매칭) ----
COMPANIES = [
    ("LS ELECTRIC",   "010120", ["LS ELECTRIC", "LS일렉트릭", "엘에스일렉트릭", "LS산전"]),
    ("효성중공업",     "298040", ["효성중공업"]),
    ("HD현대일렉트릭", "267260", ["HD현대일렉트릭", "현대일렉트릭앤에너지시스템", "현대일렉트릭"]),
    ("산일전기",       None,     ["산일전기"]),
    ("일진전기",       "103590", ["일진전기"]),
    ("대한전선",       "001440", ["대한전선"]),
    ("가온전선",       "000500", ["가온전선"]),
]

# ---- FRED ----
FRED_SERIES = [
    ("TLPWRCONS",           "미국 전력설비 건설투자", "백만USD"),
    ("PCU335311335311",     "PPI 변압기",            "지수"),
    ("PCU335313335313",     "PPI 개폐기·배전반",     "지수"),
    ("PCOPPUSDM",           "구리 (글로벌)",          "USD/톤"),
    ("IPUTIL",              "미국 유틸리티 생산",     "지수"),
    ("NEWORDER",            "미국 자본재 신규수주",   "백만USD"),
]
HEADLINE_FRED = "TLPWRCONS"

# ---- 수기 입력 항목 (API 없는 지표) ----
MANUAL_FIELDS = [
    {"k": "leadtime_us", "label": "미국 대형변압기 리드타임", "unit": "주", "d": 0},
    {"k": "goes",        "label": "방향성 전기강판(GOES)",    "unit": "USD/t", "d": 0},
    {"k": "bl_hyosung",  "label": "효성중공업 수주잔고",       "unit": "십억원", "d": 0},
    {"k": "bl_hdel",     "label": "HD현대일렉 수주잔고",       "unit": "십억원", "d": 0},
    {"k": "bl_lse",      "label": "LS ELECTRIC 수주잔고",     "unit": "십억원", "d": 0},
    {"k": "bl_sanil",    "label": "산일전기 수주잔고",         "unit": "십억원", "d": 0},
    {"k": "cu_prem",     "label": "구리 프리미엄",             "unit": "USD/t", "d": 0},
    {"k": "us_capex",    "label": "미 유틸 CAPEX 가이던스",    "unit": "십억USD", "d": 1},
]

PRESETS = [
    {"label": "기준", "p": 0, "q": 0},
    {"label": "P 강세 (단가 +20%)", "p": 20, "q": 0},
    {"label": "Q 회복 (물량 +15%)", "p": 0, "q": 15},
    {"label": "슈퍼사이클 (P+25 Q+20)", "p": 25, "q": 20},
]

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_DIR = os.path.join(HERE, "out")
CACHE_DIR = os.path.join(HERE, "cache")
STORE = os.path.join(HERE, "store.json")

STATUS = []


def log(msg):
    print(msg, flush=True)


def note(src, item, ok, n=None, err=""):
    STATUS.append({"src": src, "item": item + ((" — " + err) if err else ""), "ok": ok, "n": n})
    log(("  [OK]   " if ok else "  [FAIL] ") + src + " · " + item + (" (" + str(n) + ")" if n is not None else "") + (" :: " + err if err else ""))


def get(url, timeout=40, binary=False, retries=2):
    global _SSL_INSECURE
    last = ""
    for i in range(retries + 1):
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0 PowerPulse/1.0"})
            with urllib.request.urlopen(req, timeout=timeout, context=_SSL_CTX) as r:
                raw = r.read()
            return raw if binary else raw.decode("utf-8", "replace")
        except urllib.error.URLError as e:
            # SSL 검사 프록시 환경: 검증 실패 시 1회에 한해 검증 없는 컨텍스트로 전환
            if isinstance(getattr(e, "reason", None), ssl.SSLCertVerificationError) and not _SSL_INSECURE:
                _SSL_INSECURE = True
                globals()["_SSL_CTX"] = ssl._create_unverified_context()
                log("  [주의] SSL 인증서 검증 실패 — 이 PC의 보안 프로그램이 SSL을 검사 중으로 보입니다. 검증 없이 재시도합니다.")
                continue
            last = str(e)[:160]
            time.sleep(1.2 * (i + 1))
        except Exception as e:
            last = str(e)[:160]
            time.sleep(1.2 * (i + 1))
    raise RuntimeError(last)


def ym_shift(base, n):
    y, m = base.year, base.month - 1 + n
    y += m // 12
    m = m % 12 + 1
    return "%04d%02d" % (y, m)


# ============================================================
# 2. 관세청 — 품목별 국가별 수출입실적
# ============================================================
CUSTOMS_EP = "https://apis.data.go.kr/1220000/nitemtrade/getNitemtradeList"


def _tag(el, names):
    for n in names:
        c = el.find(n)
        if c is not None and (c.text or "").strip():
            return c.text.strip()
    return ""


def _num(el, names):
    v = _tag(el, names).replace(",", "")
    try:
        return float(v)
    except Exception:
        return None


def fetch_customs():
    """HS 4단위로 조회 → 응답의 hsCd(6단위)로 분해. year='2025.05', 총계행은 제외."""
    agg = {}
    today = dt.date.today().replace(day=1)
    windows, n = [], MONTHS_BACK
    while n > 0:
        chunk = min(11, n)
        end = ym_shift(today, -(MONTHS_BACK - n) - 1)
        start = ym_shift(today, -(MONTHS_BACK - n) - chunk)
        windows.append((start, end))
        n -= chunk

    for prefix in HS_PREFIXES:
        for cnty, cnty_kr in CNTY_TARGETS:
            got, err = 0, ""
            for start, end in windows:
                q = {"serviceKey": CUSTOMS_KEY, "strtYymm": start, "endYymm": end, "hsSgn": prefix}
                if cnty:
                    q["cntyCd"] = cnty
                try:
                    body = get(CUSTOMS_EP + "?" + urllib.parse.urlencode(q, safe=""))
                except Exception as e:
                    err = "요청실패 " + str(e)[:70]
                    break
                if "SERVICE_KEY_IS_NOT_REGISTERED" in body:
                    err = "인증키 미등록"
                    break
                if "LIMITED_NUMBER_OF_SERVICE_REQUESTS" in body:
                    err = "일일 호출한도 초과"
                    break
                try:
                    root = ET.fromstring(body)
                except Exception:
                    err = "XML 파싱실패: " + body[:70].replace("\n", " ")
                    break
                for it in root.iter("item"):
                    d = "".join(ch for ch in _tag(it, ["year"]) if ch.isdigit())
                    if len(d) != 6:
                        continue                      # '총계' 행 제외
                    hs = _tag(it, ["hsCd"])
                    if hs not in HS_MAP:
                        continue
                    usd = _num(it, ["expDlr"]) or 0
                    kg = _num(it, ["expWgt"]) or 0
                    if usd == 0 and kg == 0:
                        continue
                    # cntyCd 미지정 시 국가별로 쪼개져 올 수 있으므로 합산해서 '전체'로 집계
                    key = (d[:4] + "-" + d[4:], hs, cnty or "ALL")
                    if key not in agg:
                        item, detail, group = HS_MAP[hs]
                        agg[key] = {"ym": key[0], "hs": hs, "item": item, "detail": detail,
                                    "group": group, "cnty": key[2], "expUsd": 0.0, "expKg": 0.0}
                    agg[key]["expUsd"] += usd
                    agg[key]["expKg"] += kg
                    got += 1
                time.sleep(0.2)
            note("관세청", "HS " + prefix + "* / " + cnty_kr, err == "" and got > 0, got,
                 err or ("수집 0건" if not got else ""))
    return sorted(agg.values(), key=lambda r: (r["ym"], r["hs"], r["cnty"]))


# ============================================================
# 진단 — 실제 응답을 눈으로 확인 (python power_pulse.py --probe)
# ============================================================
def probe():
    tests = [("850423", "US", "6자리 대형변압기 / 미국"),
             ("850423", "",   "6자리 대형변압기 / 전체"),
             ("8504",   "US", "4자리 변압기 / 미국"),
             ("1001999090", "US", "공식 샘플 코드 (동작 확인용)")]
    end = ym_shift(dt.date.today().replace(day=1), -3)
    start = ym_shift(dt.date.today().replace(day=1), -14)
    for hs, cnty, label in tests:
        q = {"serviceKey": CUSTOMS_KEY, "strtYymm": start, "endYymm": end, "hsSgn": hs}
        if cnty:
            q["cntyCd"] = cnty
        url = CUSTOMS_EP + "?" + urllib.parse.urlencode(q, safe="")
        log("\n" + "=" * 58)
        log("[테스트] " + label + "  (" + start + "~" + end + ")")
        try:
            body = get(url)
        except Exception as e:
            log("  요청 실패: " + str(e)[:200])
            continue
        log(body[:1600])
        try:
            root = ET.fromstring(body)
            items = list(root.iter("item"))
            log("  --> item 개수: %d" % len(items))
            if items:
                log("  --> 필드명: " + ", ".join(c.tag for c in items[0]))
        except Exception as e:
            log("  XML 파싱 실패: " + str(e)[:120])


# ============================================================
# 3. DART — 재무 + 공시
# ============================================================
DART = "https://opendart.fss.or.kr/api/"
REPRT = [("11013", 1), ("11012", 2), ("11014", 3), ("11011", 4)]
REV_KEYS = ["매출액", "영업수익", "수익(매출액)", "매출", "영업수익(매출액)"]
OP_KEYS = ["영업이익", "영업이익(손실)", "영업손실"]


def load_corp_codes():
    path = os.path.join(CACHE_DIR, "corpCode.xml")
    fresh = os.path.exists(path) and (time.time() - os.path.getmtime(path)) < 7 * 86400
    if not fresh:
        raw = get(DART + "corpCode.xml?crtfc_key=" + DART_KEY, binary=True, timeout=90)
        if raw[:2] != b"PK":
            raise RuntimeError("zip 아님 — 키 확인: " + raw[:120].decode("utf-8", "replace"))
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            data = z.read(z.namelist()[0])
        os.makedirs(CACHE_DIR, exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
    root = ET.parse(path).getroot()
    out = []
    for e in root.iter("list"):
        out.append({
            "corp": (e.findtext("corp_code") or "").strip(),
            "name": (e.findtext("corp_name") or "").strip(),
            "stock": (e.findtext("stock_code") or "").strip(),
        })
    return out


def match_corp(table, name, stock, aliases):
    if stock:
        for r in table:
            if r["stock"] == stock:
                return r
    for a in aliases:
        for r in table:
            if r["stock"] and r["name"].replace(" ", "").upper() == a.replace(" ", "").upper():
                return r
    for a in aliases:
        for r in table:
            if r["stock"] and a.replace(" ", "") in r["name"].replace(" ", ""):
                return r
    return None


def _amt(v):
    v = (v or "").replace(",", "").strip()
    if not v or v in ("-", "—"):
        return None
    try:
        return float(v)
    except Exception:
        return None


def pick(rows, keys, field):
    for k in keys:
        for r in rows:
            nm = (r.get("account_nm") or "").replace(" ", "")
            if nm == k.replace(" ", ""):
                v = _amt(r.get(field))
                if v is not None:
                    return v
    for k in keys:
        for r in rows:
            if k.replace(" ", "") in (r.get("account_nm") or "").replace(" ", ""):
                v = _amt(r.get(field))
                if v is not None:
                    return v
    return None


def fin_full(corp_code):
    """분기(3개월) 매출·영업이익 전체 시계열(ORDER_START_YEAR~). 4Q는 연간 - 누적3Q 로 역산."""
    today = dt.date.today()
    out, cum3 = {}, {}
    yrs = list(range(ORDER_START_YEAR, today.year + 1))
    for year in yrs:
        for rc, qn in REPRT:
            for fs in ("CFS", "OFS"):
                url = (DART + "fnlttSinglAcntAll.json?crtfc_key=" + DART_KEY +
                       "&corp_code=" + corp_code + "&bsns_year=" + str(year) +
                       "&reprt_code=" + rc + "&fs_div=" + fs)
                try:
                    j = json.loads(get(url, timeout=30))
                except Exception:
                    break
                if j.get("status") != "013" and j.get("status") != "000":
                    break
                if j.get("status") != "000":
                    continue
                rows = [r for r in j.get("list", []) if r.get("sj_div") == "IS"]
                if not rows:
                    rows = [r for r in j.get("list", []) if r.get("sj_div") == "CIS"]
                if not rows:
                    continue
                rev = pick(rows, REV_KEYS, "thstrm_amount")
                op = pick(rows, OP_KEYS, "thstrm_amount")
                arev = pick(rows, REV_KEYS, "thstrm_add_amount")
                aop = pick(rows, OP_KEYS, "thstrm_add_amount")
                key = "%dQ%d" % (year, qn)
                if qn == 4:
                    c = cum3.get(year)
                    if rev is not None and c and c[0] is not None:
                        out[key] = {"q": "%d.4Q" % year, "rev": rev - c[0],
                                    "op": (op - c[1]) if (op is not None and c[1] is not None) else None}
                else:
                    if qn == 1 and rev is None:
                        rev, op = arev, aop
                    if rev is not None:
                        out[key] = {"q": "%d.%dQ" % (year, qn), "rev": rev, "op": op}
                    if qn == 3:
                        cum3[year] = (arev if arev is not None else None, aop if aop is not None else None)
                    elif qn == 1:
                        pass
                break
            time.sleep(0.12)
    return sorted(out.values(), key=lambda o: o["q"])


def fetch_fin(corp_code):
    """분기 실적 표시용 — 최근 QUARTERS_BACK 분기."""
    return fin_full(corp_code)[-QUARTERS_BACK:]


KEYWORDS = ["공급계약", "수주", "단일판매", "실적", "영업(잠정)", "유상증자", "설비투자", "시설투자", "잠정"]


def fetch_filings(corp_code, name):
    end = dt.date.today()
    bgn = end - dt.timedelta(days=FILING_DAYS)
    url = (DART + "list.json?crtfc_key=" + DART_KEY + "&corp_code=" + corp_code +
           "&bgn_de=" + bgn.strftime("%Y%m%d") + "&end_de=" + end.strftime("%Y%m%d") +
           "&page_count=100")
    j = json.loads(get(url, timeout=30))
    if j.get("status") not in ("000", "013"):
        raise RuntimeError(j.get("status", "?") + " " + str(j.get("message", ""))[:60])
    out = []
    for r in j.get("list", []):
        t = r.get("report_nm", "")
        if any(k in t for k in KEYWORDS):
            out.append({"date": r.get("rcept_dt", ""), "corp": name,
                        "title": t.strip(), "rcp": r.get("rcept_no", "")})
    return out


def load_external_financials():
    """external_financials.json — DART 재무API에 아직 없는 분기(잠정실적 등)를 임시 반영."""
    p = os.path.join(HERE, "external_financials.json")
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def fetch_dart():
    comps, filings = [], []
    try:
        table = load_corp_codes()
        note("DART", "corpCode 마스터", True, len(table))
    except Exception as e:
        note("DART", "corpCode 마스터", False, None, str(e)[:90])
        return [{"name": n, "stock": s, "quarters": []} for n, s, _ in COMPANIES], []

    for name, stock, aliases in COMPANIES:
        m = match_corp(table, name, stock, aliases)
        if not m:
            note("DART", name + " 종목매칭", False, None, "corpCode에서 못 찾음")
            comps.append({"name": name, "stock": stock or "-", "quarters": []})
            continue
        rec = {"name": name, "stock": m["stock"] or (stock or "-"), "corp": m["corp"], "quarters": []}
        try:
            rec["quarters"] = fetch_fin(m["corp"])
            note("DART", name + " 분기실적", len(rec["quarters"]) > 0, len(rec["quarters"]),
                 "" if rec["quarters"] else "재무 파싱 0건")
        except Exception as e:
            note("DART", name + " 분기실적", False, None, str(e)[:90])
        try:
            f = fetch_filings(m["corp"], name)
            filings += f
            note("DART", name + " 공시", True, len(f))
        except Exception as e:
            note("DART", name + " 공시", False, None, str(e)[:90])
        comps.append(rec)

    # 외부 잠정실적 병합(정식 재무API에 아직 없는 분기만 채움 → 정식 보고서 나오면 자동 대체)
    ext = load_external_financials()
    byname = {c["name"]: c for c in comps}
    for nm, qmap in ext.items():
        if nm.startswith("_"):
            continue
        c = byname.get(nm)
        if not c:
            continue
        have = {q["q"] for q in (c.get("quarters") or [])}
        added = 0
        for ql, vals in qmap.items():
            if ql in have:
                continue
            q = {"q": ql, "rev": vals.get("rev"), "op": vals.get("op")}
            if vals.get("prov"):
                q["prov"] = True
            c.setdefault("quarters", []).append(q)
            added += 1
        if added:
            c["quarters"] = sorted(c["quarters"], key=lambda o: o["q"])[-QUARTERS_BACK:]
            note("DART", nm + " 잠정실적(외부)", True, added)

    filings.sort(key=lambda r: r["date"], reverse=True)
    return comps, filings


# ============================================================
# 3b. DART 수주상황 — 수주잔고(직접 공시) + 신규수주(추정)
# ============================================================
# 자동 추출 회사(수주상황 표에 총 수주잔고가 잡히는 6사).
# 효성중공업(298040)은 DART 수주상황이 건설 진행률표뿐이라 전사 수주잔고 자동수집 불가 → 수동 입력.
ORDER_AUTO = {"267260", "062040", "001440", "010120", "103590", "000500"}

_UNIT_RE = re.compile(r"단위\s*[:：]\s*(억원|백만원|천원|원)")


def dart_doc(rcept):
    """정기보고서 원문(문서 XML) 텍스트. 캐시."""
    path = os.path.join(CACHE_DIR, "reports", rcept + ".txt")
    if os.path.exists(path):
        return open(path, encoding="utf-8").read()
    raw = get(DART + "document.xml?crtfc_key=" + DART_KEY + "&rcept_no=" + rcept, binary=True, timeout=90)
    if raw[:2] != b"PK":
        raise RuntimeError("문서 zip 아님")
    with zipfile.ZipFile(io.BytesIO(raw)) as z:
        s = b"".join(z.read(n) for n in z.namelist()).decode("utf-8", "replace")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as f:
        f.write(s)
    return s


def period_reports(corp_code):
    """정기보고서 → {분기라벨: rcept_no} (ORDER_START_YEAR~). 같은 분기는 최신 접수 우선."""
    url = (DART + "list.json?crtfc_key=" + DART_KEY + "&corp_code=" + corp_code +
           "&bgn_de=" + str(ORDER_START_YEAR) + "0101&end_de=" + dt.date.today().strftime("%Y%m%d") +
           "&pblntf_ty=A&page_count=100")
    j = json.loads(get(url, timeout=40))
    seen = {}
    for r in j.get("list", []):
        nm = r.get("report_nm", "")
        if not any(t in nm for t in ("분기보고서", "반기보고서", "사업보고서")):
            continue
        m = re.search(r"\((\d{4})\.(\d{2})\)", nm)
        if not m:
            continue
        q = {"03": 1, "06": 2, "09": 3, "12": 4}.get(m.group(2))
        if not q:
            continue
        lab = "%sQ%d" % (m.group(1), q)
        if lab not in seen or r["rcept_no"] > seen[lab]:
            seen[lab] = r["rcept_no"]
    return seen


def _row_amounts(row_html):
    """행 안의 콤마 숫자들(금액 후보)."""
    vals = []
    for m in re.finditer(r"<(?:TD|TH)\b[^>]*>(.*?)</(?:TD|TH)>", row_html, re.S | re.I):
        x = re.sub(r"<[^>]+>", "", m.group(1)).replace(",", "").strip()
        if re.fullmatch(r"-?\d+(?:\.\d+)?", x):
            vals.append(float(x))
    return vals


def extract_backlog(s):
    """수주상황 표에서 총 수주잔고(억원). 실패 시 None.
    관행: 수주잔고 금액은 각 데이터행의 마지막 숫자열. 합계행 있으면 그 값, 없으면 데이터행 합산."""
    tbl, pos = None, -1
    for m in re.finditer(r"<TABLE\b.*?</TABLE>", s, re.S | re.I):
        t = m.group(0)
        if (("수주잔고" in t or "수주잔액" in t) and
                ("기납품" in t or "수주총액" in t or "당기수주" in t) and "진행률" not in t):
            tbl, pos = t, m.start()
            break
    if not tbl:
        return None
    head = s[max(0, pos - 1500):pos]
    um = list(_UNIT_RE.finditer(head))
    unit = um[-1].group(1) if um else "백만원"
    rows = re.findall(r"<TR\b.*?</TR>", tbl, re.S | re.I)
    # 합계/계 행이 있으면 '마지막' 합계행(=총계)의 마지막 금액열을 쓴다.
    # (국내/해외 소계와 부문 계가 섞여 있어 첫 번째가 아니라 마지막이 전사 총계)
    tot_rows = []
    for r in rows:
        txt = re.sub(r"<[^>]+>", "", r).strip()
        if "합 계" in txt or "합계" in txt or txt.startswith("계"):
            if _row_amounts(r):
                tot_rows.append(r)
    total = None
    if tot_rows:
        total = _row_amounts(tot_rows[-1])[-1]
    else:  # 합계행 없으면 데이터행 마지막열 합산
        acc, got = 0.0, False
        for r in rows:
            txt = re.sub(r"<[^>]+>", "", r)
            if any(h in txt for h in ("수주총액", "기납품", "당기수주", "이월")) or txt.strip() in ("금액", "수량"):
                continue  # 헤더행
            v = _row_amounts(r)
            if v:
                acc += v[-1]
                got = True
        total = acc if got else None
    if total is None:
        return None
    factor = {"억원": 1.0, "백만원": 0.01, "천원": 1e-5, "원": 1e-8}.get(unit, 0.01)
    return round(total * factor, 1)


def _qkey(qlabel):
    """'2023.1Q' → '2023Q1'."""
    y, q = qlabel.split(".")
    return y + "Q" + q[0]


def load_external_orders():
    """external_orders.json — 엑셀(데이터 터미널)에서 받은 외부 수주 시계열(억원).
    DART 자동수집이 어려운 회사(효성중공업 등)와 비상장/그룹 시리즈(LS, LS전선)를 채운다."""
    p = os.path.join(HERE, "external_orders.json")
    if not os.path.exists(p):
        return {}
    try:
        return json.load(open(p, encoding="utf-8"))
    except Exception:
        return {}


def fetch_orders():
    """7사 분기별 수주잔고(억원) + 신규수주(추정=Δ잔고+당분기매출)."""
    try:
        table = load_corp_codes()
    except Exception as e:
        note("수주", "corpCode 로드", False, None, str(e)[:80])
        return []
    result = []
    for name, stock, aliases in COMPANIES:
        m = match_corp(table, name, stock, aliases)
        if not m:
            note("수주", name + " 매칭", False, None, "corpCode 못 찾음")
            result.append({"name": name, "stock": stock or "-", "mode": "manual", "quarters": []})
            continue
        corp, sc = m["corp"], (m["stock"] or stock or "-")
        # 분기 매출(억원) 맵
        rev = {}
        try:
            for o in fin_full(corp):
                if o.get("rev") is not None:
                    rev[_qkey(o["q"])] = o["rev"] / 1e8
        except Exception:
            pass
        auto = sc in ORDER_AUTO
        backlog = {}
        if auto:
            try:
                for lab, rc in sorted(period_reports(corp).items()):
                    try:
                        b = extract_backlog(dart_doc(rc))
                    except Exception:
                        b = None
                    if b is not None:
                        backlog[lab] = b
                    time.sleep(0.15)
            except Exception as e:
                note("수주", name + " 보고서목록", False, None, str(e)[:70])
        # 분기 시퀀스 구성
        labs = sorted(set(list(backlog.keys()) + list(rev.keys())))
        qs = []
        for i, lab in enumerate(labs):
            bk = backlog.get(lab)
            prev = backlog.get(labs[i - 1]) if i > 0 else None
            rv = rev.get(lab)
            no = (bk - prev + rv) if (bk is not None and prev is not None and rv is not None) else None
            if bk is None and rv is None:
                continue
            qs.append({"q": lab, "backlog": bk, "newOrders": (round(no, 1) if no is not None else None),
                       "rev": (round(rv, 1) if rv is not None else None)})
        note("수주", name + (" 자동" if auto else " 수동"),
             (len([x for x in qs if x["backlog"] is not None]) > 0) if auto else True,
             len([x for x in qs if x["backlog"] is not None]),
             "" if (auto and any(x["backlog"] is not None for x in qs)) else ("자동수집 불가 → 수기입력" if not auto else "수주잔고 0건"))
        result.append({"name": name, "stock": sc, "mode": "auto" if auto else "manual", "quarters": qs})

    # 외부 엑셀 자료 병합: 효성중공업(채움) + LS·LS전선(신규 시리즈)
    ext = load_external_orders()
    by = {c["name"]: c for c in result}
    for nm, obj in ext.items():
        qs = obj.get("quarters") or []
        nb = len([q for q in qs if q.get("backlog") is not None])
        if nm in by:
            by[nm]["quarters"] = qs
            by[nm]["mode"] = "external"
        else:
            result.append({"name": nm, "stock": obj.get("stock", "-"), "mode": "external", "quarters": qs})
        note("수주", nm + " 외부자료", nb > 0, nb, "" if nb else "외부 시계열 0건")
    return result


# ============================================================
# 4. FRED
# ============================================================
def fetch_fred():
    out = {}
    start = (dt.date.today() - dt.timedelta(days=365 * 8)).strftime("%Y-%m-%d")
    for sid, short, unit in FRED_SERIES:
        try:
            url = ("https://api.stlouisfed.org/fred/series/observations?series_id=" + sid +
                   "&api_key=" + FRED_KEY + "&file_type=json&observation_start=" + start)
            j = json.loads(get(url, timeout=40))
            obs = [{"d": o["date"], "v": float(o["value"])}
                   for o in j.get("observations", []) if o.get("value") not in (".", "", None)]
            if not obs:
                raise RuntimeError("관측치 0건")
            out[sid] = {"title": sid, "short": short, "unit": unit, "obs": obs}
            note("FRED", sid + " " + short, True, len(obs))
        except Exception as e:
            note("FRED", sid + " " + short, False, None, str(e)[:90])
        time.sleep(0.2)
    return out


# ============================================================
# 5. store 병합 (과거 데이터 보존)
# ============================================================
def merge_store(new):
    old = {}
    if os.path.exists(STORE):
        try:
            old = json.load(open(STORE, encoding="utf-8"))
        except Exception:
            old = {}
    # 관세청: (ym,hs,cnty) 키로 덮어쓰기 병합
    merged = {}
    for r in (old.get("trade") or []) + (new.get("trade") or []):
        merged[r["ym"] + "|" + r["hs"] + "|" + r["cnty"]] = r
    new["trade"] = sorted(merged.values(), key=lambda r: (r["ym"], r["hs"], r["cnty"]))
    # 재무: 회사별 분기 병합
    oldc = {c["name"]: c for c in (old.get("companies") or [])}
    for c in new.get("companies") or []:
        prev = oldc.get(c["name"], {})
        qs = {q["q"]: q for q in (prev.get("quarters") or []) + (c.get("quarters") or [])}
        c["quarters"] = sorted(qs.values(), key=lambda q: q["q"])[-QUARTERS_BACK:]
    # 공시: rcp 기준 중복 제거
    f = {r["rcp"]: r for r in (old.get("filings") or []) + (new.get("filings") or [])}
    new["filings"] = sorted(f.values(), key=lambda r: r["date"], reverse=True)[:300]
    # FRED: 새로 받은 게 있으면 교체, 실패했으면 이전 값 유지
    fr = dict(old.get("fred") or {})
    fr.update(new.get("fred") or {})
    new["fred"] = fr
    # 수주잔고·신규수주: 회사별 분기 병합(새 값 우선, 과거 잔고 보존)
    oldo = {c["name"]: c for c in (old.get("orders") or [])}
    for c in new.get("orders") or []:
        prev = oldo.get(c["name"], {})
        qs = {q["q"]: q for q in (prev.get("quarters") or [])}
        for q in (c.get("quarters") or []):
            qs[q["q"]] = q  # 신규 실행값으로 덮어쓰기
        c["quarters"] = sorted(qs.values(), key=lambda q: q["q"])
    new["orders"] = new.get("orders") or old.get("orders") or []
    # 수기 입력값 유지
    new["manual"] = new.get("manual") or old.get("manual") or {"values": {}, "prev": {}, "savedAt": None}
    with open(STORE, "w", encoding="utf-8") as fp:
        json.dump(new, fp, ensure_ascii=False)
    return new


# ============================================================
# 6. 데모 데이터
# ============================================================
def demo_orders(comps):
    import random
    random.seed(11)
    out = []
    for c in comps:
        base = random.uniform(6000, 90000)
        qs, prev = [], None
        for i, lab in enumerate(["2023Q1", "2023Q2", "2023Q3", "2023Q4", "2024Q1", "2024Q2",
                                 "2024Q3", "2024Q4", "2025Q1", "2025Q2", "2025Q3", "2025Q4", "2026Q1"]):
            bk = round(base * (1 + 0.05 * i) * (1 + 0.03 * random.uniform(-1, 1)), 1)
            rv = round(base * 0.12 * (1 + 0.02 * i), 1)
            no = round(bk - prev + rv, 1) if prev is not None else None
            qs.append({"q": lab, "backlog": bk, "newOrders": no, "rev": rv})
            prev = bk
        out.append({"name": c["name"], "stock": c.get("stock", "-"), "mode": "auto", "quarters": qs})
    return out


def demo_data():
    import math, random
    random.seed(7)
    trade = []
    base = dt.date.today().replace(day=1)
    for hs, (item, detail, group) in list(HS_MAP.items())[:8]:
        lvl = random.uniform(4e7, 2.4e8)
        for i in range(26, 0, -1):
            ym = ym_shift(base, -i)
            t = (26 - i) / 26.0
            for cnty, _ in CNTY_TARGETS:
                mult = 0.42 if cnty == "US" else 1.0
                usd = lvl * mult * (1 + 0.55 * t) * (1 + 0.09 * math.sin(i / 2.3))
                kg = usd / (9 + 7 * t + random.uniform(-0.6, 0.6))
                trade.append({"ym": ym[:4] + "-" + ym[4:], "hs": hs, "item": item, "detail": detail,
                              "group": group, "cnty": cnty or "ALL",
                              "expUsd": round(usd), "expKg": round(kg)})
    comps = []
    for n, s, _ in COMPANIES:
        r0 = random.uniform(2e11, 1.1e12)
        qs = []
        for i in range(8):
            y = 2024 + (i + 2) // 4
            q = (i + 2) % 4 + 1
            rv = r0 * (1 + 0.05 * i)
            qs.append({"q": "%d.%dQ" % (y, q), "rev": rv, "op": rv * (0.07 + 0.012 * i)})
        comps.append({"name": n, "stock": s or "062040", "quarters": qs})
    fred = {}
    for sid, short, unit in FRED_SERIES:
        v0 = random.uniform(80, 160)
        obs = []
        for i in range(60, 0, -1):
            d = (base - dt.timedelta(days=30 * i))
            obs.append({"d": d.strftime("%Y-%m-01"), "v": round(v0 * (1 + 0.011 * (60 - i)) * (1 + 0.02 * math.sin(i / 4)), 2)})
        fred[sid] = {"title": sid, "short": short, "unit": unit, "obs": obs}
    fil = [{"date": (dt.date.today() - dt.timedelta(days=3 * i)).strftime("%Y%m%d"),
            "corp": COMPANIES[i % 7][0], "title": "단일판매·공급계약 체결 (예시 데이터)", "rcp": "demo%03d" % i}
           for i in range(12)]
    note("DEMO", "합성 데이터 (실제 수치 아님)", True, len(trade))
    return trade, comps, fil, fred


# ============================================================
# 7. main
# ============================================================
def main():
    if "--probe" in sys.argv:
        probe()
        return
    demo = "--demo" in sys.argv
    os.makedirs(OUT_DIR, exist_ok=True)
    os.makedirs(CACHE_DIR, exist_ok=True)
    log("=" * 58)
    log("Power Equipment Pulse 빌드 " + ("[데모 모드]" if demo else ""))
    log("=" * 58)

    if demo:
        trade, comps, filings, fred = demo_data()
    else:
        log("[1/3] 관세청 수출입 수집...")
        try:
            trade = fetch_customs()
        except Exception as e:
            trade = []
            note("관세청", "전체", False, None, str(e)[:90])
        log("[2/3] DART 재무·공시 수집...")
        try:
            comps, filings = fetch_dart()
        except Exception as e:
            comps, filings = [], []
            note("DART", "전체", False, None, str(e)[:90])
        log("[3/4] FRED 미국 지표 수집...")
        try:
            fred = fetch_fred()
        except Exception as e:
            fred = {}
            note("FRED", "전체", False, None, str(e)[:90])
        log("[4/4] DART 수주잔고·신규수주 수집...")
        try:
            orders = fetch_orders()
        except Exception as e:
            orders = []
            note("수주", "전체", False, None, str(e)[:90])

    payload = {"trade": trade, "companies": comps, "filings": filings, "fred": fred,
               "orders": (orders if not demo else demo_orders(comps))}
    if not demo:
        payload = merge_store(payload)

    yms = sorted({r["ym"] for r in payload.get("trade") or []})
    as_of = yms[-1] if yms else dt.date.today().strftime("%Y-%m")
    payload.update({
        "asOf": as_of,
        "generatedAt": dt.datetime.now().strftime("%Y-%m-%d %H:%M"),
        "headline": "Power Equipment Pulse — 수출 P·Q, 실적, 미국 수요를 한 화면에서",
        "cntyLabel": {"US": "미국", "ALL": "전체"},
        "headlineFred": HEADLINE_FRED,
        "manualFields": MANUAL_FIELDS,
        "manual": payload.get("manual") or {"values": {}, "prev": {}, "savedAt": None},
        "presets": PRESETS,
        "baseFx": BASE_FX,
        "status": STATUS,
    })

    sys.path.insert(0, HERE)
    from template import HTML
    html = HTML.replace("/*__DATA__*/{}", json.dumps(payload, ensure_ascii=False, separators=(",", ":")))
    name = "전력기기_대시보드_" + dt.date.today().strftime("%Y%m%d") + (".demo" if demo else "") + ".html"
    path = os.path.join(OUT_DIR, name)
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)
    # 고정 이름 사본(항상 최신) — 이 파일로 공유 링크를 만들면 링크가 안 바뀐다.
    if not demo:
        latest = os.path.join(OUT_DIR, "전력기기_대시보드_최신.html")
        with open(latest, "w", encoding="utf-8") as f:
            f.write(html)
        log("최신본(고정): " + latest)

    ok = sum(1 for s in STATUS if s["ok"])
    log("-" * 58)
    log("완료 — 성공 %d / 실패 %d" % (ok, len(STATUS) - ok))
    log("수출 데이터 %d행 · 기준월 %s" % (len(payload.get("trade") or []), as_of))
    log("산출물: " + path)
    log("이 HTML 파일만 공유하세요. API 키는 들어있지 않습니다.")
    return path


if __name__ == "__main__":
    main()
