import importlib
import os

from . import vmulti_idx
from . import vmulti_kr
from . import vmulti_us
from . import vcompare_idx
from . import vret_idx
from . import vret_kr
from . import vret_us
from . import vfinance_kr
from . import vheatmap_idx
from . import vtreemap_us
from . import vheatmap_kr
from . import vheatmap_us
from . import vtargetprice_us


def _set_korean_font():
    try:
        fm = importlib.import_module("matplotlib.font_manager")
        plt = importlib.import_module("matplotlib.pyplot")
    except ImportError:
        return None

    font_paths = [
        "/usr/share/fonts/truetype/nanum/NanumGothic.ttf",
        "/usr/share/fonts/truetype/nanum/NanumBarunGothic.ttf",
        "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc",
        "/usr/share/fonts/opentype/noto/NotoSansCJKkr-Regular.otf",
        "C:/Windows/Fonts/malgun.ttf",
        "C:/Windows/Fonts/malgunbd.ttf",
        "/System/Library/Fonts/AppleSDGothicNeo.ttc",
        "/Library/Fonts/AppleGothic.ttf",
    ]

    for font_path in font_paths:
        if os.path.exists(font_path):
            fm.fontManager.addfont(font_path)
            font_name = fm.FontProperties(fname=font_path).get_name()
            plt.rcParams["font.family"] = font_name
            plt.rcParams["axes.unicode_minus"] = False
            return font_name

    plt.rcParams["axes.unicode_minus"] = False
    return None


class Visual:
    def __init__(self):
        self.korean_font = _set_korean_font()

    def multi_idx(self):
        vmulti_idx.multi_idx()

    def multi_kr(self):
        vmulti_kr.multi_kr()
        
    def multi_us(self):
        vmulti_us.multi_us()

    def compare_idx(self):
        vcompare_idx.compare_idx()

    def ret_idx(self):
        vret_idx.ret_idx()

    def ret_kr(self):
        vret_kr.ret_kr()
        
    def ret_us(self):
        vret_us.ret_us()

    def finance_kr(self):
        vfinance_kr.finance_kr()

    def heatmap_idx(self):
        vheatmap_idx.heatmap_idx()

    def treemap_us(self):
        vtreemap_us.treemap_us()

    def heatmap_kr(self):
        vheatmap_kr.heatmap_kr()

    def heatmap_us(self):
        vheatmap_us.heatmap_us()

    def targetprice_us(self):
        vtargetprice_us.targetprice_us()
