#!/usr/bin/env python3
"""
gen_pdf_web.py - Xuất CV ra PDF A4 với layout MÔ PHỎNG GIAO DIỆN WEB (index.html).

Bản "anh em" của gen_pdf.py. Cùng dựng thủ công bằng ReportLab (không cần Chromium),
nhưng phong cách bám sát trang web: hero có ảnh + dòng terminal, ô thống kê số liệu
teal, thanh kỹ năng (progress bar), card kinh nghiệm/dự án, tag cloud và cả mục
"Chuyện nghề" vốn chỉ có trên web. gen_pdf.py thì gọn kiểu CV in truyền thống.

Cài đặt:
    pip install -r requirements.txt

Chạy:
    python gen_pdf_web.py                 # -> Duong_Van_Giang_CV_web.pdf
    python gen_pdf_web.py -o cv.pdf       # đổi tên file xuất ra
    python gen_pdf_web.py --no-photo      # bỏ ảnh chân dung
"""
from __future__ import annotations

import argparse
import base64
import sys
from pathlib import Path

for _stream in (sys.stdout, sys.stderr):
    try:
        _stream.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT = Path(__file__).resolve().parent
AVATAR = ROOT / "avatar.jpg"
PHONE_ENC = "MDk4MTkyMTE2OA=="

ACCENT = "#0a8d82"
ACCENT_LT = "#0fb5a6"
INK = "#0e2a28"
SOFT = "#51635f"
LINE = "#dbe7e5"
SURFACE = "#ffffff"
BG_ALT = "#eef6f5"
CHIP_BG = "#e3f4f1"
TRACK = "#e3eceb"


# ── Font ────────────────────────────────────────────────────────────────────
def register_fonts():
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    win = Path("C:/Windows/Fonts")
    candidates = [
        (win / "arial.ttf", win / "arialbd.ttf", win / "ariali.ttf", win / "arialbi.ttf"),
        (win / "segoeui.ttf", win / "segoeuib.ttf", win / "segoeuii.ttf", win / "segoeuiz.ttf"),
        (win / "tahoma.ttf", win / "tahomabd.ttf", win / "tahoma.ttf", win / "tahomabd.ttf"),
        (Path("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Oblique.ttf"),
         Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-BoldOblique.ttf")),
        (Path("/Library/Fonts/Arial.ttf"), Path("/Library/Fonts/Arial Bold.ttf"),
         Path("/Library/Fonts/Arial Italic.ttf"), Path("/Library/Fonts/Arial Bold Italic.ttf")),
    ]
    mono_candidates = [win / "consola.ttf",
                       Path("/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"),
                       Path("/Library/Fonts/Courier New.ttf")]
    base = "CVFont"
    chosen = None
    for reg, bold, ital, bi in candidates:
        if reg.exists() and bold.exists():
            chosen = (reg, bold, ital, bi)
            break
    if not chosen:
        sys.exit("Không tìm thấy font Unicode.")
    reg, bold, ital, bi = chosen
    pdfmetrics.registerFont(TTFont(base, str(reg)))
    pdfmetrics.registerFont(TTFont(base + "-Bold", str(bold)))
    pdfmetrics.registerFont(TTFont(base + "-Italic", str(ital if ital.exists() else reg)))
    pdfmetrics.registerFont(TTFont(base + "-BoldItalic", str(bi if bi.exists() else bold)))
    pdfmetrics.registerFontFamily(base, normal=base, bold=base + "-Bold",
                                  italic=base + "-Italic", boldItalic=base + "-BoldItalic")
    mono = "CVMono"
    for m in mono_candidates:
        if m.exists():
            pdfmetrics.registerFont(TTFont(mono, str(m)))
            break
    else:
        mono = base
    return base, base + "-Bold", mono


# ── Dữ liệu CV ──────────────────────────────────────────────────────────────
def cv_data(phone: str) -> dict:
    return {
        "name": "Dương Văn Giang",
        "role_grad": "Senior Fullstack Developer",
        "role_rest": "Dev Lead",
        "tagline": ("Java Spring Boot · Angular · Oracle PL/SQL - gần 7 năm tại IDNES "
                    "(Dự án Đấu thầu qua mạng Quốc gia), trong đó gần 4 năm ở vai trò Dev Lead."),
        "chips": ["giangdv97@gmail.com", phone, "22/10/1997", "Nam",
                  "giangdv97.pro", "github.com/giangdv1997", "Hà Nội, Việt Nam"],
        "stats": [
            ("7", "Năm kinh nghiệm Fullstack"),
            ("4", "Năm Dev Lead, đồng hành cùng team 15 người"),
            ("10tr+", "Bản ghi xử lý trên Oracle PL/SQL"),
            ("99.9%", "Uptime, vận hành 24/7"),
        ],
        "about": [
            "Tôi hướng tới vai trò <b>Back-End / Technical Lead</b> cho các hệ thống giao dịch "
            "quy mô lớn, thời gian thực và vận hành 24/7 - nơi đề cao độ ổn định, hiệu năng và "
            "xử lý dữ liệu lớn. Tôi tìm một môi trường để vừa trực tiếp giải các bài toán kỹ thuật "
            "khó, vừa đồng hành cùng đội ngũ và chịu trách nhiệm cho chất lượng vận hành sản phẩm; "
            "song song đó tiếp tục đưa <b>AI vào quy trình phát triển</b> để nâng năng suất. Định "
            "hướng này khớp với những bài toán <b>VETC</b> đang giải, và đó là lý do tôi muốn "
            "<b>ứng tuyển vào VETC</b>.",
        ],
        "skills": [
            ("Front-End", [("Angular 8–14+ / TypeScript", 90), ("NgRx · RxJS", 85),
                           ("WebSocket / STOMP (realtime)", 80),
                           ("Angular Material · PrimeNG · Ng-Zorro", 85),
                           ("OAuth2/OIDC · JWT · RBAC", 82), ("React · Next.js", 78),
                           ("HTML5 · CSS3 · SCSS · Bootstrap", 90)]),
            ("Back-End", [("Java EE / SE (8, 11, 17)", 90),
                          ("Spring Boot · Spring MVC · Spring Cloud", 90),
                          ("JHipster · Microservices", 85),
                          ("RabbitMQ · Redisson (khoá phân tán) · Redis", 85),
                          ("Hibernate / JPA · RESTful API", 88),
                          ("OAuth2 · JWT (Spring Security)", 82),
                          ("Node.js · TypeScript · Quartz", 90)]),
            ("Database", [("Oracle 10g–19c · PL/SQL", 95),
                          ("Package · Function · Job · Trigger · DBLink", 90),
                          ("PostgreSQL · MySQL", 82),
                          ("Tối ưu truy vấn · Dữ liệu chục triệu bản ghi", 90),
                          ("Thiết kế CSDL (DB Design)", 90), ("pgvector", 50)]),
            ("DevOps & Tools", [("Git · SVN · CI/CD", 90),
                                ("RedHat Linux · OpenShift (OKD)", 85),
                                ("Build · Merge · Deploy Production", 90),
                                ("Docker · Jib", 80), ("JUnit 5 · Kiểm thử tự động", 80),
                                ("Review & Merge code (toàn dự án)", 90)]),
        ],
        "ai_card": ("AI & Tự động hoá quy trình",
                    "Tự xây công cụ AI để tăng năng suất - qua 3 giai đoạn tìm hiểu và ứng dụng "
                    "AI vào công việc. Nắm và áp dụng kiến trúc agent: tool-calling/ReAct, "
                    "plan-execute, sub-agents, memory & context engineering, tích hợp multi-LLM.",
                    ["jira-auto-agent", "→", "maestro", "→", "detebu"],
                    ["Claude", "Cursor", "Trae", "DeepSeek", "AI Agents", "Prompt Engineering"]),
        "tags": ["Java", "Spring Boot", "Spring Cloud", "JHipster", "Microservices", "RabbitMQ",
                 "Redisson", "Node.js", "Angular", "NgRx", "React", "TypeScript", "WebSocket",
                 "OAuth2/JWT", "Oracle PL/SQL", "PostgreSQL", "MySQL", "pgvector", "Redis",
                 "Hibernate", "Prisma", "DB Design", "Docker", "OpenShift/OKD", "CI/CD",
                 "Code Review", "Dữ liệu lớn"],
        "experience": [
            {
                "title": "Dev Lead (Technical Lead)",
                "date": "2023 – nay (gần 4 năm)",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "Lập kế hoạch & điều phối công việc cho <b>team 15 lập trình viên</b>; quản lý tiến độ các bản build.",
                    "Lập plan triển khai phần mới khi <b>thay đổi Thông tư / nghiệp vụ</b> đấu thầu.",
                    "<b>Đầu mối giải đáp vướng mắc kỹ thuật</b> cho team, trực tiếp xử lý các issue khó.",
                    "Phản biện tài liệu từ <b>BA</b> - đánh giá tính khả thi trước khi triển khai.",
                    "<b>Review & merge code cho toàn bộ dự án</b>; lập checklist build, merge & deploy production - đóng gói <b>Docker/Jib</b> lên <b>OpenShift</b>.",
                    "Vận hành production: kiểm tra log trên <b>OpenShift (OKD)</b>, xử lý sự cố.",
                ],
                "tags": ["Leadership", "Code Review", "OpenShift/OKD", "CI/CD"],
            },
            {
                "title": "Senior Fullstack Developer",
                "date": "2021 – 2023",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "<b>Phụ trách chính phân hệ eBid</b>: Dự án, Kế hoạch LCNT, TBMT, Tổ chuyên gia, lập & trình phê duyệt HSMT, KQLCNT.",
                    "Tự xây dựng <b>cả phân hệ SPM</b> (FE + BE) và toàn bộ <b>back-end phân hệ Báo cáo Thống kê</b> (thiên về xử lý SQL).",
                    "<b>Thiết kế cơ sở dữ liệu</b> cho các phân hệ eBid, Thống kê & SPM.",
                    "Xây dựng <b>job/API thống kê cho C12 – Bộ Tài chính</b>: package, function, job trên bảng <b>chục triệu bản ghi</b>.",
                    "Trong <b>microservices</b> (nền tảng <b>JHipster</b>): Redisson khoá phân tán, RabbitMQ hàng đợi, Quartz job định kỳ.",
                ],
                "tags": ["Angular", "Spring Boot", "Oracle PL/SQL", "DB Design"],
            },
            {
                "title": "Fullstack Developer",
                "date": "Cuối 2019 – 2021",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "Bắt đầu tại dự án; phát triển tính năng Front-End (<b>Angular</b>) và Back-End (<b>Spring Boot</b>) trên Hệ thống Đấu thầu qua mạng Quốc gia.",
                    "Làm quen nghiệp vụ đấu thầu, kiến trúc hệ thống và quy trình build/release.",
                ],
                "tags": ["Angular", "Spring Boot", "Oracle"],
            },
        ],
        "projects": [
            ("eBid - Phân hệ nghiệp vụ trọng tâm", "Owner", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Phụ trách toàn bộ nghiệp vụ cốt lõi: Dự án, LCNT, TBMT, Tổ chuyên gia, HSMT, KQLCNT - kèm thiết kế CSDL."),
            ("Phân hệ SPM", "Fullstack", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Tự xây trọn vẹn từ giao diện Angular đến back-end Spring Boot và thiết kế CSDL - làm chủ end-to-end."),
            ("Phân hệ Báo cáo & Thống kê", "Backend", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Toàn bộ back-end cho phân hệ báo cáo; nghiệp vụ thiên về SQL, tối ưu truy vấn dữ liệu lớn."),
            ("Job API Thống kê - C12", "Backend · Data", "C12 - Bộ Tài chính",
             "Job/API tổng hợp dữ liệu đấu thầu; SQL phức tạp bằng package, function & job trên bảng chục triệu bản ghi."),
            ("Bộ công cụ AI tự động hoá", "Cá nhân", "jira-auto-agent · maestro · detebu",
             "Ba thế hệ công cụ tự xây: tool thuần → maestro (Node/TS, Express + Socket.IO, hybrid "
             "router token+LLM) → detebu (harness, multi-LLM Claude/OpenAI/Gemini/DeepSeek, sub-agents)."),
            ("Module cơ sở phân hệ UM & CT", "Backend", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Module nền tảng dùng chung cho UM (Quản lý người dùng) và CT - phục vụ các phân hệ khác tái sử dụng."),
        ],
        "metrics": [("99.9%", "Uptime hệ thống"), ("5 năm", "Nhân viên xuất sắc liên tục"),
                    ("4/5", "Điểm đánh giá hàng tháng")],
        "achievements": [
            "<b>Nhân viên xuất sắc 5 năm liền</b>: cấp khối EP (2021–2024), lên cấp FIS năm 2025.",
            "Điểm đánh giá hiệu suất hàng tháng luôn đạt <b>≥ 4/5</b>.",
            "Nhiều lần được <b>thưởng nóng</b> (cá nhân & đội nhóm) từ quản lý.",
            "Giữ hệ thống vận hành ổn định, <b>hạn chế tối đa sự cố</b> gây nghẽn luồng nghiệp vụ.",
        ],
        "education": "Trường Đại học Công nghiệp Hà Nội - Cử nhân Công nghệ thông tin",
        "strengths": [
            "Nắm chắc nghiệp vụ đấu thầu (LCNT · HSMT · KQLCNT) từ đầu đến cuối",
            "Oracle PL/SQL mạnh: package/function/job trên dữ liệu chục triệu bản ghi",
            "Gần 4 năm Dev Lead: lên plan, phân việc team 15, review & merge cả dự án",
            "Vận hành production (OpenShift/OKD), xử lý sự cố",
            "Tự xây công cụ AI agent (multi-LLM), đưa AI vào quy trình phát triển",
        ],
        "languages": [("Tiếng Việt", "Bản ngữ"), ("Tiếng Anh", "Đọc & viết tài liệu kỹ thuật tốt")],
        "references": [("Bành Trọng Văn", "Trưởng phòng Vận hành và phát triển ứng dụng, IDNES", "VanBT8@fpt.com"),
                       ("La Văn Phi", "Nguyên Phó phòng Vận hành và phát triển ứng dụng, IDNES", "PhiLV2@fpt.com")],
        "stories": [
            ("Đêm trước mỗi lần golive Thông tư",
             "Cứ mỗi đợt Thông tư mới đổi nghiệp vụ, cả team gần như thức trắng để kịp golive "
             "đúng hạn. Khổ nhất là build front-end - project Angular phình to quá cỡ, build lỗi "
             "lên lỗi xuống, sửa xong lại ngồi chờ mòn mỏi cả chục phút mới biết qua hay chưa. Cà "
             "phê, màn hình đầy log, tiếng bàn phím tới sáng - rồi khi hệ thống lên production "
             "chạy mượt, bao mệt mỏi tự nhiên tan hết."),
            ("Con bug lúc 10 giờ đêm",
             "Có hôm 10 giờ đêm, dính một con bug oái oăm - tự mình code, rồi tự mình gặp. Ngồi "
             "debug nát cả code, lật từng dòng, thử đủ cách vẫn không ra. Cuối cùng hoá ra lỗi "
             "chẳng nằm ở mình, mà ở chính thư viện đang dùng. Lúc tìm ra vừa nhẹ nhõm vừa tức "
             "cười - mất mấy tiếng chỉ để phát hiện mình… không sai."),
            ("Bầu trời mới mang tên AI",
             "Ngày một người anh giấu mặt (tên Như) mang AI vào dự án, mình như nhìn thấy một bầu "
             "trời hoàn toàn mới. Hoá ra cách mình làm việc bao năm có thể thay đổi tận gốc. Mê "
             "tới mức tận dụng từng chút token, “bào” cho bằng cạn gói mới thôi - vừa tò mò, vừa "
             "hơi choáng, mà cuốn hút lạ thường."),
            ("Khoảnh khắc vỡ lẽ",
             "Đến lúc tự tay viết con tool AI agent đầu tiên, mình mới thật sự “vỡ lẽ”: không chỉ "
             "dùng AI, mình hoàn toàn có thể tự build ra tay chân cho nó. Càng đào sâu càng tiếp thu được nhiều - "
             "nhìn lại mới thấy ngày đầu mình ngây thơ tới mức nào. Có giai đoạn còn bị ChatGPT "
             "“gài” cho mơ mộng tự build một SaaS để đời, đã tính nghỉ việc đang làm; rồi vỡ mộng, "
             "và đó lại là bài học đáng giá nhất - tiền không đến từ sản phẩm “tốt”, mà từ sản "
             "phẩm giải quyết được một nỗi đau thật của người dùng. Chặng đường từ jira-auto-agent "
             "tới detebu là chuỗi những lần vỡ lẽ như thế - và mình vẫn đang đi tiếp."),
        ],
    }


def _photo(ImageCls, box_w, box_h):
    """Đặt ảnh vào khung box_w×box_h, GIỮ NGUYÊN TỈ LỆ gốc để không bị méo."""
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(AVATAR)).getSize()
    r = min(box_w / iw, box_h / ih)
    return ImageCls(str(AVATAR), width=iw * r, height=ih * r)


def build(output: Path, with_photo: bool) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY, TA_CENTER
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
        TableStyle, Image, KeepTogether, Flowable,
    )


    from reportlab.platypus import Flowable as _FL

    class _Icon(_FL):
        """Icon vector vẽ tay (line-style, màu accent) - giống icon SVG trên web."""
        def __init__(self, name, size, color):
            super().__init__()
            self.name, self.size, self.color = name, size, color
        def wrap(self, *a):
            return self.size, self.size
        def draw(self):
            c, S, n = self.canv, self.size, self.name
            c.setStrokeColor(self.color); c.setFillColor(self.color)
            c.setLineWidth(max(0.6, S * 0.085)); c.setLineCap(1); c.setLineJoin(1)
            if n == "email":
                c.roundRect(0, S*0.24, S, S*0.52, S*0.1, stroke=1, fill=0)
                p = c.beginPath(); p.moveTo(S*0.06, S*0.72); p.lineTo(S*0.5, S*0.47); p.lineTo(S*0.94, S*0.72); c.drawPath(p)
            elif n == "phone":
                c.roundRect(S*0.3, S*0.05, S*0.4, S*0.9, S*0.1, stroke=1, fill=0)
                c.circle(S*0.5, S*0.155, S*0.045, stroke=0, fill=1)
            elif n == "calendar":
                c.roundRect(0, S*0.04, S, S*0.74, S*0.1, stroke=1, fill=0)
                c.line(0, S*0.56, S, S*0.56)
                c.line(S*0.28, S*0.78, S*0.28, S*0.96); c.line(S*0.72, S*0.78, S*0.72, S*0.96)
            elif n == "user":
                c.circle(S*0.5, S*0.72, S*0.19, stroke=1, fill=0)
                p = c.beginPath(); p.moveTo(S*0.13, S*0.05); p.curveTo(S*0.2, S*0.46, S*0.8, S*0.46, S*0.87, S*0.05); c.drawPath(p)
            elif n == "globe":
                c.circle(S*0.5, S*0.5, S*0.45, stroke=1, fill=0)
                c.line(S*0.05, S*0.5, S*0.95, S*0.5)
                c.ellipse(S*0.31, S*0.05, S*0.69, S*0.95, stroke=1, fill=0)
            elif n == "github":
                r = S*0.12
                c.circle(S*0.26, S*0.2, r, stroke=1, fill=0)
                c.circle(S*0.26, S*0.8, r, stroke=1, fill=0)
                c.circle(S*0.74, S*0.46, r, stroke=1, fill=0)
                c.line(S*0.26, S*0.32, S*0.26, S*0.68)
                p = c.beginPath(); p.moveTo(S*0.26, S*0.5); p.curveTo(S*0.5, S*0.5, S*0.62, S*0.5, S*0.62, S*0.5); c.drawPath(p)
                c.line(S*0.62, S*0.5, S*0.66, S*0.48)
            elif n == "location":
                c.circle(S*0.5, S*0.64, S*0.27, stroke=1, fill=0)
                p = c.beginPath(); p.moveTo(S*0.27, S*0.52); p.lineTo(S*0.5, S*0.04); p.lineTo(S*0.73, S*0.52); c.drawPath(p)
                c.circle(S*0.5, S*0.64, S*0.085, stroke=0, fill=1)

    reg, bold, mono = register_fonts()
    phone = base64.b64decode(PHONE_ENC).decode()
    data = cv_data(phone)

    C = lambda h: colors.HexColor(h)
    accent, accent_lt = C(ACCENT), C(ACCENT_LT)
    ink, soft, line_c = C(INK), C(SOFT), C(LINE)
    surface, bg_alt, chip_bg, track = C(SURFACE), C(BG_ALT), C(CHIP_BG), C(TRACK)

    PAGE_W, PAGE_H = A4
    LM = RM = 13 * mm
    TM, BM = 12 * mm, 11 * mm
    CW = PAGE_W - LM - RM

    # ── styles ──
    def ps(name, **kw):
        return ParagraphStyle(name, **kw)
    name_st = ps("nm", fontName=bold, fontSize=23, leading=26, textColor=ink)
    hello_st = ps("hl", fontName=mono, fontSize=8.5, leading=11, textColor=accent)
    role_st = ps("rl", fontName=bold, fontSize=12.5, leading=15, textColor=accent_lt)
    tag_st = ps("tg", fontName=reg, fontSize=8.7, leading=12.5, textColor=soft)
    kicker_st = ps("kk", fontName=bold, fontSize=7.6, leading=10, textColor=accent_lt)
    title_st = ps("tt", fontName=bold, fontSize=14.5, leading=17, textColor=ink)
    body = ps("bd", fontName=reg, fontSize=8.9, leading=13, textColor=ink, alignment=TA_JUSTIFY)
    bullet_st = ps("bl", fontName=reg, fontSize=8.5, leading=12, textColor=ink)
    job_st = ps("jb", fontName=bold, fontSize=10.5, leading=12.5, textColor=ink)
    date_st = ps("dt", fontName=bold, fontSize=8, leading=10, textColor=accent, alignment=2)
    org_st = ps("og", fontName="CVFont-Italic", fontSize=8, leading=10.5, textColor=soft)
    statnum = ps("sn", fontName=bold, fontSize=18, leading=19, textColor=accent, alignment=TA_CENTER)
    statlbl = ps("sl", fontName=reg, fontSize=6.9, leading=8.4, textColor=soft, alignment=TA_CENTER)
    projt = ps("pt", fontName=bold, fontSize=9.4, leading=11.5, textColor=ink)
    projmeta = ps("pm", fontName=bold, fontSize=7.4, leading=9.5, textColor=accent)
    projbody = ps("pb", fontName=reg, fontSize=8, leading=10.6, textColor=soft)
    small = ps("sm", fontName=reg, fontSize=8.5, leading=12, textColor=ink)
    skcat = ps("sc", fontName=bold, fontSize=9.6, leading=12, textColor=ink)
    chip_ps = ps("cp", fontName=reg, fontSize=7.6, leading=9.5, textColor=ink)
    tag_ps = ps("tp", fontName=bold, fontSize=7.4, leading=9.5, textColor=accent, alignment=TA_CENTER)

    # ── Flowable: thanh kỹ năng (label + progress bar) ──
    class Bars(Flowable):
        def __init__(self, items, width):
            super().__init__()
            self.items, self.width = items, width
            self.rowh = 15.5
        def wrap(self, aw, ah):
            self.height = len(self.items) * self.rowh
            return self.width, self.height
        def draw(self):
            c = self.canv
            y = self.height
            for label, lvl in self.items:
                y -= self.rowh
                c.setFont(reg, 7.8)
                c.setFillColor(ink)
                c.drawString(0, y + 5.5, label)
                c.setFont(bold, 7.2)
                c.setFillColor(accent)
                c.drawRightString(self.width, y + 5.5, f"{lvl}%")
                # track
                bw, bh = self.width, 3.2
                c.setFillColor(track)
                c.roundRect(0, y + 0.5, bw, bh, bh / 2, stroke=0, fill=1)
                c.setFillColor(accent)
                c.roundRect(0, y + 0.5, bw * lvl / 100.0, bh, bh / 2, stroke=0, fill=1)

    story = []

    # ── HERO ─────────────────────────────────────────────────────────────────
    hero_txt = [
        Paragraph("~/cv $ whoami", hello_st),
        Spacer(1, 2),
        Paragraph(data["name"], name_st),
        Paragraph(f'{data["role_grad"]}  ·  {data["role_rest"]}', role_st),
        Spacer(1, 2),
        Paragraph(data["tagline"], tag_st),
    ]
    if with_photo and AVATAR.exists():
        img = _photo(Image, 30 * mm, 30 * mm)
        img.hAlign = "CENTER"
        hero = Table([[img, hero_txt]], colWidths=[34 * mm, CW - 34 * mm])
        hero.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (0, 0), 2), ("LEFTPADDING", (1, 0), (1, 0), 8),
            ("RIGHTPADDING", (-1, -1), (-1, -1), 2),
            ("TOPPADDING", (0, 0), (-1, -1), 4), ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
            ("BACKGROUND", (0, 0), (-1, -1), surface),
            ("BOX", (0, 0), (-1, -1), 0.8, line_c),
            ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ]))
    else:
        hero = Table([[hero_txt]], colWidths=[CW])
        hero.setStyle(TableStyle([
            ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6), ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("BACKGROUND", (0, 0), (-1, -1), surface), ("BOX", (0, 0), (-1, -1), 0.8, line_c),
            ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
        ]))
    story.append(hero)
    story.append(Spacer(1, 5))

    # ── chips liên hệ (pills) ──
    chip_icons = ["email", "phone", "calendar", "user", "globe", "github", "location"]
    def _url_for(name, text):
        if name == "email":  return "mailto:" + text
        if name == "phone":  return "tel:" + text.replace(" ", "")
        if name == "globe":  return "https://" + text.rstrip("/") + "/"
        if name == "github": return "https://" + text
        return None
    def _chip(name, text):
        href = _url_for(name, text)
        ptxt = f'<a href="{href}" color="{INK}">{text}</a>' if href else text
        cell = Table([[_Icon(name, 10, accent), Paragraph(ptxt, chip_ps)]], colWidths=[14, None])
        cell.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 3),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        return cell
    chip_cells = [_chip(chip_icons[i], t) for i, t in enumerate(data["chips"])]
    per = 4
    chip_rows = [chip_cells[i:i + per] for i in range(0, len(chip_cells), per)]
    for r in chip_rows:
        while len(r) < per:
            r.append("")
    cct = Table(chip_rows, colWidths=[CW / per] * per)
    cct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), chip_bg),
        ("INNERGRID", (0, 0), (-1, -1), 3, colors.white),
        ("BOX", (0, 0), (-1, -1), 3, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 7), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(cct)
    story.append(Spacer(1, 6))

    # ── stat cards ──
    def stat_grid(items, num_style, lbl_style, ncols=None):
        ncols = ncols or len(items)
        cells = [[Paragraph(n, num_style), Spacer(1, 1), Paragraph(l, lbl_style)] for n, l in items]
        t = Table([cells], colWidths=[CW / ncols] * ncols)
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), bg_alt),
            ("INNERGRID", (0, 0), (-1, -1), 4, colors.white),
            ("BOX", (0, 0), (-1, -1), 4, colors.white),
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("TOPPADDING", (0, 0), (-1, -1), 7), ("BOTTOMPADDING", (0, 0), (-1, -1), 7),
            ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
        ]))
        return t
    story.append(stat_grid(data["stats"], statnum, statlbl))
    story.append(Spacer(1, 9))

    # ── 01 GIỚI THIỆU ──
    story.append(_sec("01 - Giới thiệu", "Mục tiêu nghề nghiệp", CW, kicker_st, title_st,
                      Table, TableStyle, Paragraph, accent))
    story.append(Spacer(1, 4))
    for p in data["about"]:
        story.append(Paragraph(p, body))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 5))

    # ── 02 KỸ NĂNG (cards 2x2 với bars) ──
    story.append(_sec("02 - Năng lực", "Kỹ năng công nghệ", CW, kicker_st, title_st,
                      Table, TableStyle, Paragraph, accent))
    story.append(Spacer(1, 5))
    half = (CW - 7) / 2
    inner_w = half - 16
    sk_cards = []
    for cat, items in data["skills"]:
        sk_cards.append([Paragraph(cat, skcat), Spacer(1, 4), Bars(items, inner_w)])
    sk_grid = [[sk_cards[0], sk_cards[1]], [sk_cards[2], sk_cards[3]]]
    skt = Table(sk_grid, colWidths=[half, half])
    skt.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), surface),
        ("BOX", (0, 0), (-1, -1), 7, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 7, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 8), ("RIGHTPADDING", (0, 0), (-1, -1), 8),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 10),
        ("LINEBELOW", (0, 0), (-1, 0), 7, colors.white),
    ]))
    # outer border via wrapper
    sk_outer = Table([[skt]], colWidths=[CW])
    sk_outer.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0),
                                  ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0),
                                  ("BOTTOMPADDING", (0, 0), (-1, -1), 0)]))
    story.append(sk_outer)
    story.append(Spacer(1, 6))

    # AI card (wide)
    aic = data["ai_card"]
    ai_inner = [
        Paragraph(aic[0], skcat),
        Spacer(1, 2),
        Paragraph(aic[1], projbody),
        Spacer(1, 4),
        Paragraph("  ".join(f'<font color="{ACCENT}"><b>{x}</b></font>' if x != "→"
                            else '<font color="#9bb3ae">→</font>' for x in aic[2]),
                  ps("aiflow", fontName=reg, fontSize=8.2, leading=11, textColor=ink)),
        Spacer(1, 3),
        Paragraph("   ".join(f'<font color="{ACCENT}">{t}</font>' for t in aic[3]),
                  ps("aitools", fontName=bold, fontSize=7.8, leading=10, textColor=accent)),
    ]
    ai_t = Table([[ai_inner]], colWidths=[CW])
    ai_t.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), bg_alt),
        ("BOX", (0, 0), (-1, -1), 0.8, line_c),
        ("LINEBEFORE", (0, 0), (0, -1), 3, accent_lt),
        ("LEFTPADDING", (0, 0), (-1, -1), 10), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(ai_t)
    story.append(Spacer(1, 6))

    # tag cloud
    tcells = [Paragraph(t, tag_ps) for t in data["tags"]]
    cols = 5
    trows = [tcells[i:i + cols] for i in range(0, len(tcells), cols)]
    for r in trows:
        while len(r) < cols:
            r.append("")
    tct = Table(trows, colWidths=[CW / cols] * cols)
    tct.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), chip_bg),
        ("INNERGRID", (0, 0), (-1, -1), 3, colors.white),
        ("BOX", (0, 0), (-1, -1), 3, colors.white),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3), ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
    ]))
    story.append(tct)
    story.append(Spacer(1, 9))

    # ── 03 KINH NGHIỆM (timeline cards) ──
    story.append(_sec("03 - Hành trình", "Kinh nghiệm làm việc", CW, kicker_st, title_st,
                      Table, TableStyle, Paragraph, accent))
    story.append(Spacer(1, 5))
    for job in data["experience"]:
        top = Table([[Paragraph(job["title"], job_st), Paragraph(job["date"], date_st)]],
                    colWidths=[CW * 0.66 - 16, CW * 0.34 - 16])
        top.setStyle(TableStyle([("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                                 ("LEFTPADDING", (0, 0), (-1, -1), 0),
                                 ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                 ("TOPPADDING", (0, 0), (-1, -1), 0),
                                 ("BOTTOMPADDING", (0, 0), (-1, -1), 2)]))
        blist = [Paragraph(f'<font color="{ACCENT}">▸</font> {b}', bullet_st) for b in job["bullets"]]
        tagline = Paragraph("   ".join(f'<font color="{ACCENT}"><b>{t}</b></font>' for t in job["tags"]),
                            ps("jt", fontName=bold, fontSize=7.4, leading=10, textColor=accent))
        inner = [top, Paragraph(job["org"], org_st), Spacer(1, 3)] + blist + [Spacer(1, 3), tagline]
        card = Table([[inner]], colWidths=[CW])
        card.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), surface),
            ("BOX", (0, 0), (-1, -1), 0.8, line_c),
            ("LINEBEFORE", (0, 0), (0, -1), 3, accent),
            ("LEFTPADDING", (0, 0), (-1, -1), 12), ("RIGHTPADDING", (0, 0), (-1, -1), 10),
            ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
        ]))
        story.append(KeepTogether([card, Spacer(1, 6)]))

    # ── 04 DỰ ÁN ──
    story.append(_sec("04 - Sản phẩm", "Dự án tiêu biểu", CW, kicker_st, title_st,
                      Table, TableStyle, Paragraph, accent))
    story.append(Spacer(1, 5))
    pcells = []
    for title, role, client, desc in data["projects"]:
        pcells.append([Paragraph(title, projt),
                       Paragraph(f"{role}  ·  {client}", projmeta),
                       Spacer(1, 2), Paragraph(desc, projbody)])
    pgrid = []
    for i in range(0, len(pcells), 2):
        pair = pcells[i:i + 2]
        if len(pair) == 1:
            pair.append([])
        pgrid.append(pair)
    pj = Table(pgrid, colWidths=[half, half])
    pj.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), surface),
        ("BOX", (0, 0), (-1, -1), 7, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 7, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    pj_outer = Table([[pj]], colWidths=[CW])
    pj_outer.setStyle(TableStyle([("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
                                  ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
                                  ("LINEBEFORE", (0, 0), (0, -1), 0, colors.white)]))
    story.append(pj_outer)
    story.append(Spacer(1, 9))

    # ── 05 THÀNH TÍCH ──
    story.append(KeepTogether([
        _sec("05 - Ghi nhận", "Thành tích nổi bật", CW, kicker_st, title_st,
             Table, TableStyle, Paragraph, accent),
        Spacer(1, 5),
        stat_grid(data["metrics"], statnum, statlbl),
        Spacer(1, 5),
        Table([[ [Paragraph(f'<font color="{ACCENT}">▸</font> {a}', bullet_st) for a in data["achievements"]] ]],
              colWidths=[CW], style=TableStyle([
                  ("LEFTPADDING", (0, 0), (-1, -1), 2), ("RIGHTPADDING", (0, 0), (-1, -1), 2),
                  ("TOPPADDING", (0, 0), (-1, -1), 2), ("BOTTOMPADDING", (0, 0), (-1, -1), 1)])),
        Spacer(1, 8),
    ]))

    # ── 06 HỌC VẤN (3 cột) ──
    col1 = [Paragraph("Học vấn", skcat), Spacer(1, 3), Paragraph(data["education"], small)]
    col2 = [Paragraph("Thế mạnh nổi bật", skcat), Spacer(1, 3)] + \
           [Paragraph(f'<font color="{ACCENT}">▸</font> {s}', bullet_st) for s in data["strengths"]]
    col3 = [Paragraph("Ngoại ngữ", skcat), Spacer(1, 3)] + \
           [Paragraph(f'<b>{l}</b><br/><font color="#51635f">{lv}</font>', small) for l, lv in data["languages"]]
    edu = Table([[col1, col2, col3]], colWidths=[CW * 0.28, CW * 0.44, CW * 0.28])
    edu.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), surface),
        ("BOX", (0, 0), (-1, -1), 0.8, line_c),
        ("LINEAFTER", (0, 0), (0, -1), 0.6, line_c),
        ("LINEAFTER", (1, 0), (1, -1), 0.6, line_c),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(KeepTogether([
        _sec("06 - Nền tảng", "Học vấn & Thế mạnh", CW, kicker_st, title_st,
             Table, TableStyle, Paragraph, accent),
        Spacer(1, 5), edu, Spacer(1, 8),
    ]))

    # ── 07 CHUYỆN NGHỀ (web-only) ──
    st_cells = []
    for stitle, stext in data["stories"]:
        st_cells.append([Paragraph(stitle, projt), Spacer(1, 2), Paragraph(stext, projbody)])
    sgrid = []
    for i in range(0, len(st_cells), 2):
        pair = st_cells[i:i + 2]
        if len(pair) == 1:
            pair.append([])
        sgrid.append(pair)
    sg = Table(sgrid, colWidths=[half, half])
    sg.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("BACKGROUND", (0, 0), (-1, -1), bg_alt),
        ("BOX", (0, 0), (-1, -1), 7, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 7, colors.white),
        ("LEFTPADDING", (0, 0), (-1, -1), 9), ("RIGHTPADDING", (0, 0), (-1, -1), 9),
        ("TOPPADDING", (0, 0), (-1, -1), 8), ("BOTTOMPADDING", (0, 0), (-1, -1), 8),
    ]))
    story.append(_sec("07 - Bên lề", "Chuyện nghề ở IDNES", CW, kicker_st, title_st,
                      Table, TableStyle, Paragraph, accent))
    story.append(Spacer(1, 5))
    story.append(sg)
    story.append(Spacer(1, 9))

    # ── 08 LIÊN HỆ / THAM CHIẾU ──
    refs = [Paragraph(f'<b>{n}</b> - {r}  ·  <a href="mailto:{m}" color="{ACCENT}">{m}</a>', small)
            for n, r, m in data["references"]]
    story.append(KeepTogether([
        _sec("08 - Kết nối", "Người tham chiếu", CW, kicker_st, title_st,
             Table, TableStyle, Paragraph, accent),
        Spacer(1, 4), *refs,
    ]))

    # ── footer ──
    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(reg, 7.3)
        canvas.setFillColor(soft)
        canvas.drawString(LM, 7 * mm, "Dương Văn Giang - Senior Fullstack Developer · Dev Lead")
        canvas.drawRightString(PAGE_W - RM, 7 * mm, f"Trang {doc.page}")
        canvas.setStrokeColor(line_c)
        canvas.line(LM, 9.5 * mm, PAGE_W - RM, 9.5 * mm)
        canvas.restoreState()

    frame = Frame(LM, BM, CW, PAGE_H - TM - BM, id="m",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc = BaseDocTemplate(str(output), pagesize=A4, leftMargin=LM, rightMargin=RM,
                          topMargin=TM, bottomMargin=BM, title="CV - Dương Văn Giang",
                          author="Dương Văn Giang")
    doc.addPageTemplates([PageTemplate(id="cv", frames=[frame], onPage=footer)])
    doc.build(story)
    print(f"Done: {output.name}  ({output.stat().st_size/1024:.0f} KB)  ->  {output}")


def _sec(kicker, title, CW, kicker_st, title_st, Table, TableStyle, Paragraph, accent):
    t = Table([[Paragraph(kicker.upper(), kicker_st)], [Paragraph(title, title_st)]],
              colWidths=[CW])
    t.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (0, 0), 0), ("BOTTOMPADDING", (0, 0), (0, 0), 1),
        ("TOPPADDING", (0, 1), (0, 1), 0), ("BOTTOMPADDING", (0, 1), (0, 1), 2),
        ("LINEBELOW", (0, 1), (-1, 1), 1.4, accent),
    ]))
    return t


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="Duong_Van_Giang_CV_web.pdf")
    ap.add_argument("--no-photo", action="store_true")
    args = ap.parse_args()
    build((ROOT / args.output).resolve(), with_photo=not args.no_photo)


if __name__ == "__main__":
    main()
