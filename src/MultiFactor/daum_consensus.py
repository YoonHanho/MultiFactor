"""다음증권 추정실적 컨센서스를 연간/분기 DataFrame으로 가져옵니다."""

import json
import re
import time
import ssl
from urllib.parse import urlencode
from urllib.request import Request, urlopen
from urllib.error import URLError

import pandas as pd
import numpy as np

CONSENSUS_URL = "https://wisefn.finance.daum.net/v1/company/cF1002.aspx"
CONSENSUS_COLUMNS = [
    "FY-end",
    "주재무제표",
    "매출액 (억원)",
    "YoY (%)",
    "영업이익 (억원)",
    "당기순이익 (억원)",
    "EPS (원)",
    "PER (배)",
    "PBR (배)",
    "ROE (%)",
    "EV/EBITDA (배)",
    "순부채 비율 (%)",
]
DATA_BLOCK_PATTERN = re.compile(
    r'\{\s*tid\s*:\s*"(?P<tab>TB_[01])"\s*,\s*'
    r"dest\s*:\s*(?P<rows>\[\[.*?\]\])\s*\}",
    re.DOTALL,
)
STOCK_CODE_PATTERN = re.compile(r"(?:A)?\d{6}")

COLUMN_MAP = {
    "매출액 (억원)": "매출액",
    "영업이익 (억원)": "영업이익",
    "당기순이익 (억원)": "당기순이익",
    "PER (배)": "PER(배)",
    "PBR (배)": "PBR(배)",
    "ROE (%)": "ROE(%)",
}


def get_daum_consensus(
    stock_code: str = "A005930",
    timeout: float = 15,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """다음증권에서 종목의 연간·분기 컨센서스를 가져옵니다."""
    clean_code = str(stock_code).strip()
    if not STOCK_CODE_PATTERN.fullmatch(clean_code):
        clean_code = clean_code.zfill(6)
        if not STOCK_CODE_PATTERN.fullmatch(clean_code):
            raise ValueError(f"올바르지 않은 종목코드 형식입니다: {stock_code}")

    company_code = clean_code.removeprefix("A")
    query = urlencode({"cmp_cd": company_code, "finGubun": "MAIN"})
    request = Request(
        f"{CONSENSUS_URL}?{query}",
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/130.0.0.0 Safari/537.36"
            ),
            "Referer": f"https://finance.daum.net/quotes/A{company_code}",
            "Accept": "text/html,application/xhtml+xml",
        },
    )
    html = None
    max_retries = 3
    last_err = None

    for attempt in range(max_retries):
        try:
            with urlopen(request, timeout=timeout) as response:
                html = response.read().decode(
                    response.headers.get_content_charset() or "utf-8"
                )
            break
        except (URLError, ssl.SSLError, ConnectionError, OSError) as e:
            last_err = e
            if attempt < max_retries - 1:
                time.sleep(1.0)
            else:
                raise last_err

    rows_by_tab = {
        match.group("tab"): json.loads(match.group("rows"))
        for match in DATA_BLOCK_PATTERN.finditer(html)
    }
    if "TB_0" not in rows_by_tab or "TB_1" not in rows_by_tab:
        raise ValueError(
            "응답에서 연간/분기 컨센서스를 찾지 못했습니다. "
            "다음증권 페이지의 데이터 형식이 변경되었을 수 있습니다."
        )

    def to_dataframe(rows: list[list[str]]) -> pd.DataFrame:
        if any(len(row) != len(CONSENSUS_COLUMNS) for row in rows):
            raise ValueError("컨센서스 데이터의 열 구성이 예상과 다릅니다.")
        frame = pd.DataFrame(rows, columns=CONSENSUS_COLUMNS)
        for column in CONSENSUS_COLUMNS[2:]:
            values = frame[column].str.replace(",", "", regex=False)
            frame[column] = pd.to_numeric(values, errors="coerce")
        return frame

    annual = to_dataframe(rows_by_tab["TB_0"])
    quarterly = to_dataframe(rows_by_tab["TB_1"])
    return annual, quarterly


def get_daum_finstate(stock_code: str, freq: str = "Y", timeout: float = 15) -> pd.DataFrame:
    """
    다음증권 컨센서스를 수집하여 기존 SnapDataReader와 호환되는 컬럼 및 인덱스 구조로 반환합니다.
    - freq: 'Y' (연간) 또는 'Q' (분기)
    """
    annual_df, quarterly_df = get_daum_consensus(stock_code=stock_code, timeout=timeout)
    is_annual = freq.upper().endswith("Y") or freq.upper() == "Y"
    df = annual_df.copy() if is_annual else quarterly_df.copy()

    if "FY-end" in df.columns:
        df.set_index("FY-end", inplace=True)
        df.index.name = "날짜"

    # 기존 SnapDataReader 컬럼명('매출액', '영업이익', 'PER(배)' 등) 매핑 추가
    for orig_col, target_col in COLUMN_MAP.items():
        if orig_col in df.columns:
            df[target_col] = df[orig_col]

    return df
