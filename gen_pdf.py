#!/usr/bin/env python3
"""
gen_pdf.py - Xuất CV ra PDF A4, dựng layout THỦ CÔNG bằng ReportLab.

Trước đây script render index.html bằng Chromium (Playwright). Bản này KHÔNG cần
trình duyệt: nội dung CV nhúng thẳng trong file, layout do code vẽ bằng ReportLab
(Platypus) -> nhẹ, nhanh, ổn định, tự xuống trang và đánh số trang.

Đây là bản CV in GỌN, truyền thống. Muốn bản bám sát giao diện web (hero, stat
card, thanh kỹ năng, tag cloud, mục "Chuyện nghề") thì dùng gen_pdf_web.py.

Cài đặt:
    pip install -r requirements.txt

Chạy:
    python gen_pdf.py                  # -> Duong_Van_Giang_CV.pdf
    python gen_pdf.py -o cv.pdf        # đổi tên file xuất ra
    python gen_pdf.py --no-photo       # bỏ ảnh chân dung
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
LINE = "#d7e3e1"
CHIP_BG = "#e8f6f4"


def register_fonts() -> tuple[str, str]:
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
    for reg, bold, ital, bi in candidates:
        if not (reg.exists() and bold.exists()):
            continue
        base = "CVFont"
        pdfmetrics.registerFont(TTFont(base, str(reg)))
        pdfmetrics.registerFont(TTFont(base + "-Bold", str(bold)))
        ital = ital if ital.exists() else reg
        bi = bi if bi.exists() else bold
        pdfmetrics.registerFont(TTFont(base + "-Italic", str(ital)))
        pdfmetrics.registerFont(TTFont(base + "-BoldItalic", str(bi)))
        pdfmetrics.registerFontFamily(
            base, normal=base, bold=base + "-Bold",
            italic=base + "-Italic", boldItalic=base + "-BoldItalic",
        )
        return base, base + "-Bold"
    sys.exit("Không tìm thấy font Unicode.")


def cv_data(phone: str) -> dict:
    return {
        "name": "Dương Văn Giang",
        "role": "Senior Fullstack Developer · Dev Lead",
        "tagline": ("Java Spring Boot · Angular · Oracle PL/SQL - gần 7 năm tại IDNES "
                    "(Dự án Đấu thầu qua mạng Quốc gia), trong đó gần 4 năm ở vai trò Dev Lead."),
        "contacts": [
            ("Email", "giangdv97@gmail.com"),
            ("Điện thoại", phone),
            ("Ngày sinh", "22/10/1997"),
            ("Website", "giangdv97.pro"),
            ("GitHub", "github.com/giangdv1997"),
            ("Địa chỉ", "Hà Nội, Việt Nam"),
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
            ("Front-End", "Angular 8–14+ / TypeScript · NgRx · RxJS · WebSocket/STOMP · Angular "
                          "Material · PrimeNG · Ng-Zorro · OAuth2/OIDC · JWT · React · Next.js · "
                          "HTML5 · CSS3 · SCSS · Bootstrap"),
            ("Back-End", "Java EE/SE (8, 11, 17) · Spring Boot · Spring MVC · Spring Cloud · "
                         "JHipster · Microservices · RabbitMQ · Redisson (khoá phân tán) · Redis · "
                         "Hibernate/JPA · RESTful API · OAuth2/JWT · Node.js · TypeScript · Quartz"),
            ("Database", "Oracle 10g–19c · PL/SQL · Package · Function · Job · Trigger · DBLink · "
                         "PostgreSQL · MySQL · Tối ưu truy vấn (chục triệu bản ghi) · Thiết kế CSDL · pgvector"),
            ("DevOps & Tools", "Git · SVN · CI/CD · RedHat Linux · OpenShift (OKD) · "
                               "Build/Merge/Deploy Production · Docker · Jib · JUnit 5 · Review & Merge code"),
            ("AI & Tự động hoá", "Tự xây công cụ AI agent qua 3 giai đoạn: jira-auto-agent → "
                                 "maestro (Node/TS · Express+Socket.IO · hybrid router LLM) → detebu "
                                 "(harness · multi-LLM Claude/OpenAI/Gemini/DeepSeek · sub-agents). "
                                 "Claude · Cursor · Trae · DeepSeek · Prompt Engineering"),
        ],
        "experience": [
            {
                "title": "Dev Lead (Technical Lead)",
                "date": "2023 – nay (gần 4 năm)",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "Lập kế hoạch & điều phối công việc cho <b>team 15 lập trình viên</b>; quản lý tiến độ các bản build.",
                    "Lập plan triển khai các phần mới khi <b>thay đổi Thông tư / nghiệp vụ</b> đấu thầu.",
                    "<b>Đầu mối giải đáp vướng mắc kỹ thuật</b> cho team, trực tiếp xử lý các issue khó.",
                    "Làm việc với các team khác để gỡ vướng cho team dev trong quá trình vận hành.",
                    "Phản biện tài liệu từ <b>BA</b> - đánh giá tính khả thi trước khi triển khai.",
                    "<b>Review & merge code cho toàn bộ dự án</b>; lập checklist build, merge & deploy production - đóng gói <b>Docker/Jib</b> lên <b>OpenShift</b>.",
                    "Vận hành production: kiểm tra log trên <b>OpenShift (OKD)</b>, xử lý sự cố.",
                ],
            },
            {
                "title": "Senior Fullstack Developer",
                "date": "2021 – 2023",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "<b>Phụ trách chính phân hệ eBid</b>: Dự án, Kế hoạch LCNT, Thông báo mời thầu "
                    "(TBMT), Tổ chuyên gia, lập & trình phê duyệt HSMT, Kết quả lựa chọn nhà thầu (KQLCNT).",
                    "Tự xây dựng <b>cả phân hệ SPM</b> (Front-End + Back-End) và toàn bộ <b>back-end "
                    "phân hệ Báo cáo Thống kê</b> (thiên về xử lý SQL).",
                    "<b>Thiết kế cơ sở dữ liệu</b> cho các phân hệ eBid, Thống kê & SPM.",
                    "Tham gia xây dựng <b>job/API thống kê đấu thầu cho C12 – Bộ Tài chính</b>: "
                    "package, function, job xử lý bảng <b>hàng chục triệu bản ghi</b>.",
                    "Trong hệ <b>microservices</b> (nền tảng <b>JHipster</b>): <b>Redisson</b> xử lý "
                    "race condition (khoá phân tán), <b>RabbitMQ</b> hàng đợi fire-and-forget & gọi "
                    "chéo service, <b>Quartz</b> chạy job/báo cáo định kỳ.",
                    "Front-End <b>Angular + TypeScript</b>, Back-End <b>Java Spring Boot</b>, <b>Oracle PL/SQL</b>.",
                ],
            },
            {
                "title": "Fullstack Developer",
                "date": "Cuối 2019 – 2021",
                "org": "FPT Information System (FIS) · IDNES - Dự án Đấu thầu qua mạng Quốc gia",
                "bullets": [
                    "Bắt đầu tại dự án; phát triển tính năng Front-End (<b>Angular</b>) và Back-End "
                    "(<b>Spring Boot</b>) trên Hệ thống Đấu thầu qua mạng Quốc gia.",
                    "Làm quen nghiệp vụ đấu thầu, kiến trúc hệ thống và quy trình build/release.",
                ],
            },
        ],
        "projects": [
            ("eBid - Phân hệ nghiệp vụ trọng tâm", "Owner", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Phụ trách toàn bộ nghiệp vụ cốt lõi: Dự án, Kế hoạch LCNT, TBMT, Tổ chuyên gia, "
             "lập & trình phê duyệt HSMT, KQLCNT - kèm thiết kế CSDL."),
            ("Phân hệ SPM", "Fullstack", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Tự xây dựng trọn vẹn một phân hệ từ giao diện Angular đến back-end Spring Boot và "
             "thiết kế cơ sở dữ liệu - làm chủ end-to-end."),
            ("Phân hệ Báo cáo & Thống kê", "Backend", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Xây dựng toàn bộ back-end cho phân hệ báo cáo thống kê; nghiệp vụ thiên về SQL, "
             "tối ưu truy vấn trên khối dữ liệu lớn."),
            ("Job API Thống kê Đấu thầu - C12", "Backend · Data", "C12 - Bộ Tài chính",
             "Xây dựng job/API tổng hợp dữ liệu đấu thầu; SQL phức tạp bằng package, function & "
             "job trên bảng hàng chục triệu bản ghi."),
            ("Bộ công cụ AI tự động hoá", "Cá nhân", "jira-auto-agent · maestro · detebu",
             "Ba thế hệ công cụ tự xây: jira-auto-agent (tool thuần) → maestro (orchestrator AI cho "
             "Dev Lead - Node/TS, Express + Socket.IO, hybrid router token + LLM, confirm trước mọi "
             "write) → detebu (AI agent harness kiểu Claude Code - multi-LLM Claude/OpenAI/Gemini/"
             "DeepSeek, sub-agents, memory & context compaction, tích hợp Jira/OpenShift/GitLab)."),
            ("Module cơ sở phân hệ UM & CT", "Backend", "Hệ thống Đấu thầu qua mạng Quốc gia",
             "Xây dựng các module nền tảng dùng chung cho phân hệ UM (Quản lý người dùng) và CT - "
             "phục vụ các phân hệ nghiệp vụ khác kế thừa & tái sử dụng."),
        ],
        "achievements": [
            "<b>Nhân viên xuất sắc 5 năm liền</b>: cấp khối EP (2021–2024), lên cấp FIS năm 2025 - "
            "<i>EP & FIS thuộc FPT Information System (FIS)</i>.",
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
        "languages": [
            ("Tiếng Việt", "Bản ngữ"),
            ("Tiếng Anh", "Đọc & viết tài liệu kỹ thuật tốt"),
        ],
        "references": [
            ("Bành Trọng Văn", "Trưởng phòng Vận hành và phát triển ứng dụng, IDNES", "VanBT8@fpt.com"),
            ("La Văn Phi", "Nguyên Phó phòng Vận hành và phát triển ứng dụng, IDNES", "PhiLV2@fpt.com"),
        ],
    }


def _photo(ImageCls, box_w, box_h):
    """Đặt ảnh vào khung box_w x box_h, GIỮ NGUYÊN TỈ LỆ gốc để không bị méo."""
    from reportlab.lib.utils import ImageReader
    iw, ih = ImageReader(str(AVATAR)).getSize()
    r = min(box_w / iw, box_h / ih)
    return ImageCls(str(AVATAR), width=iw * r, height=ih * r)


def build(output: Path, with_photo: bool) -> None:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.units import mm
    from reportlab.lib import colors
    from reportlab.lib.enums import TA_JUSTIFY
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.platypus import (
        BaseDocTemplate, PageTemplate, Frame, Paragraph, Spacer, Table,
        TableStyle, Image, KeepTogether, ListFlowable, ListItem,
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

    reg, bold = register_fonts()
    phone = base64.b64decode(PHONE_ENC).decode()
    data = cv_data(phone)

    accent = colors.HexColor(ACCENT)
    ink = colors.HexColor(INK)
    soft = colors.HexColor(SOFT)
    line_c = colors.HexColor(LINE)
    chip = colors.HexColor(CHIP_BG)

    name_st = ParagraphStyle("name", fontName=bold, fontSize=21, leading=24, textColor=ink, spaceAfter=2)
    role_st = ParagraphStyle("role", fontName=bold, fontSize=11.5, leading=14, textColor=accent, spaceAfter=5)
    tag_st = ParagraphStyle("tag", fontName=reg, fontSize=8.6, leading=12.5, textColor=soft)
    sec_st = ParagraphStyle("sec", fontName=bold, fontSize=11.5, leading=13, textColor=colors.white)
    body = ParagraphStyle("body", fontName=reg, fontSize=9, leading=13.2, textColor=ink, alignment=TA_JUSTIFY)
    bullet_st = ParagraphStyle("bullet", fontName=reg, fontSize=8.8, leading=12.4, textColor=ink)
    job_st = ParagraphStyle("job", fontName=bold, fontSize=10, leading=12, textColor=ink)
    date_st = ParagraphStyle("date", fontName=bold, fontSize=8.4, leading=11, textColor=accent, alignment=2)
    org_st = ParagraphStyle("org", fontName="CVFont-Italic", fontSize=8.4, leading=11, textColor=soft, spaceAfter=2)
    proj_t = ParagraphStyle("projt", fontName=bold, fontSize=9.2, leading=11.5, textColor=ink)
    proj_meta = ParagraphStyle("projm", fontName=bold, fontSize=7.6, leading=10, textColor=accent)
    proj_body = ParagraphStyle("projb", fontName=reg, fontSize=8.2, leading=11, textColor=soft)
    small = ParagraphStyle("small", fontName=reg, fontSize=8.6, leading=12, textColor=ink)
    skill_cat = ParagraphStyle("skcat", fontName=bold, fontSize=8.8, leading=11.5, textColor=accent)
    skill_val = ParagraphStyle("skval", fontName=reg, fontSize=8.6, leading=11.8, textColor=ink)

    PAGE_W, PAGE_H = A4
    LM = RM = 14 * mm
    TM = 13 * mm
    BM = 12 * mm
    content_w = PAGE_W - LM - RM

    def section(title: str) -> Table:
        t = Table([[Paragraph(title.upper(), sec_st)]], colWidths=[content_w])
        t.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), accent),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 3.5),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4.5),
        ]))
        return t

    def bullets(items):
        return ListFlowable(
            [ListItem(Paragraph(b, bullet_st), value="•", leftIndent=12, spaceBefore=1.5) for b in items],
            bulletType="bullet", bulletColor=accent, bulletFontName=bold,
            bulletFontSize=8.8, leftIndent=6, spaceBefore=1, spaceAfter=0,
        )

    story: list = []

    head_text = [Paragraph(data["name"], name_st),
                 Paragraph(data["role"], role_st),
                 Paragraph(data["tagline"], tag_st)]
    if with_photo and AVATAR.exists():
        img = _photo(Image, 26 * mm, 26 * mm)
        img.hAlign = "CENTER"
        head = Table([[img, head_text]], colWidths=[30 * mm, content_w - 30 * mm])
        head.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (0, 0), 0),
            ("LEFTPADDING", (1, 0), (1, 0), 6),
            ("RIGHTPADDING", (-1, -1), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        story.append(head)
    else:
        story.extend(head_text)
    story.append(Spacer(1, 5))

    ct_style = ParagraphStyle("ct", fontName=reg, fontSize=8.2, leading=10.5, textColor=ink)
    icon_map = {"Email": "email", "Điện thoại": "phone", "Ngày sinh": "calendar",
                "Website": "globe", "GitHub": "github", "Địa chỉ": "location"}
    def _href(label, val):
        if label == "Email":      return "mailto:" + val
        if label == "Điện thoại": return "tel:" + val.replace(" ", "")
        if label == "Website":    return "https://" + val.rstrip("/") + "/"
        if label == "GitHub":     return "https://" + val
        return None
    contact_cells = []
    for label, val in data["contacts"]:
        href = _href(label, val)
        vtxt = f'<a href="{href}" color="{INK}">{val}</a>' if href else val
        cell = Table([[_Icon(icon_map[label], 9.5, accent), Paragraph(vtxt, ct_style)]],
                     colWidths=[13, None])
        cell.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0), ("RIGHTPADDING", (0, 0), (0, 0), 3),
            ("RIGHTPADDING", (1, 0), (1, 0), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0), ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ]))
        contact_cells.append(cell)
    rows = [contact_cells[i:i + 3] for i in range(0, len(contact_cells), 3)]
    ct = Table(rows, colWidths=[content_w / 3] * 3)
    ct.setStyle(TableStyle([
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("TOPPADDING", (0, 0), (-1, -1), 1.5),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 1.5),
        ("LINEABOVE", (0, 0), (-1, 0), 1, accent),
        ("LINEBELOW", (0, -1), (-1, -1), 0.6, line_c),
    ]))
    story.append(ct)
    story.append(Spacer(1, 7))

    story.append(section("01 - Mục tiêu nghề nghiệp"))
    story.append(Spacer(1, 4))
    for p in data["about"]:
        story.append(Paragraph(p, body))
        story.append(Spacer(1, 3))
    story.append(Spacer(1, 4))

    story.append(section("02 - Kỹ năng công nghệ"))
    story.append(Spacer(1, 4))
    sk_rows = [[Paragraph(cat, skill_cat), Paragraph(val, skill_val)] for cat, val in data["skills"]]
    sk = Table(sk_rows, colWidths=[32 * mm, content_w - 32 * mm])
    sk.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
        ("RIGHTPADDING", (0, 0), (0, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LINEBELOW", (0, 0), (-1, -2), 0.5, line_c),
    ]))
    story.append(sk)
    story.append(Spacer(1, 8))

    story.append(section("03 - Kinh nghiệm làm việc"))
    story.append(Spacer(1, 4))
    for job in data["experience"]:
        top = Table([[Paragraph(job["title"], job_st), Paragraph(job["date"], date_st)]],
                    colWidths=[content_w * 0.62, content_w * 0.38])
        top.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
            ("LEFTPADDING", (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING", (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 1),
        ]))
        block = [top, Paragraph(job["org"], org_st), bullets(job["bullets"]), Spacer(1, 6)]
        story.append(KeepTogether(block))

    story.append(section("04 - Dự án tiêu biểu"))
    story.append(Spacer(1, 4))
    proj_cells = []
    for title, role, client, desc in data["projects"]:
        proj_cells.append([
            Paragraph(title, proj_t),
            Paragraph(f"{role}  ·  {client}", proj_meta),
            Spacer(1, 2),
            Paragraph(desc, proj_body),
        ])
    grid = []
    for i in range(0, len(proj_cells), 2):
        pair = proj_cells[i:i + 2]
        if len(pair) == 1:
            pair.append([])
        grid.append(pair)
    half = (content_w - 6) / 2
    pj = Table(grid, colWidths=[half, half])
    pj.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
        ("BACKGROUND", (0, 0), (-1, -1), colors.HexColor("#f4faf9")),
        ("BOX", (0, 0), (-1, -1), 4, colors.white),
        ("INNERGRID", (0, 0), (-1, -1), 4, colors.white),
        ("LINEBEFORE", (0, 0), (-1, -1), 2, accent),
    ]))
    story.append(pj)
    story.append(Spacer(1, 8))

    story.append(KeepTogether([
        section("05 - Thành tích nổi bật"),
        Spacer(1, 4),
        bullets(data["achievements"]),
        Spacer(1, 8),
    ]))

    edu_block = [
        section("06 - Học vấn & Thế mạnh"),
        Spacer(1, 4),
        Paragraph(f'<font color="{ACCENT}"><b>Học vấn:</b></font> {data["education"]}', small),
        Spacer(1, 3),
        Paragraph(f'<font color="{ACCENT}"><b>Thế mạnh nổi bật</b></font>', small),
        bullets(data["strengths"]),
        Spacer(1, 3),
        Paragraph('<font color="%s"><b>Ngoại ngữ:</b></font> %s' % (
            ACCENT, "  ·  ".join(f"{l} ({lv})" for l, lv in data["languages"])), small),
        Spacer(1, 8),
    ]
    story.append(KeepTogether(edu_block))

    ref_lines = [Paragraph(f'<b>{n}</b> - {r}  ·  <font color="{ACCENT}">{m}</font>', small)
                 for n, r, m in data["references"]]
    story.append(KeepTogether([
        section("07 - Người tham chiếu"),
        Spacer(1, 4),
        *ref_lines,
    ]))

    def footer(canvas, doc):
        canvas.saveState()
        canvas.setFont(reg, 7.5)
        canvas.setFillColor(soft)
        canvas.drawString(LM, 7 * mm, "Dương Văn Giang - Senior Fullstack Developer · Dev Lead")
        canvas.drawRightString(PAGE_W - RM, 7 * mm, f"Trang {doc.page}")
        canvas.setStrokeColor(line_c)
        canvas.line(LM, 10 * mm, PAGE_W - RM, 10 * mm)
        canvas.restoreState()

    frame = Frame(LM, BM, content_w, PAGE_H - TM - BM, id="main",
                  leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    doc = BaseDocTemplate(str(output), pagesize=A4,
                          leftMargin=LM, rightMargin=RM, topMargin=TM, bottomMargin=BM,
                          title="CV - Dương Văn Giang", author="Dương Văn Giang")
    doc.addPageTemplates([PageTemplate(id="cv", frames=[frame], onPage=footer)])
    doc.build(story)
    print(f"Done: {output.name}  ({output.stat().st_size/1024:.0f} KB)  ->  {output}")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("-o", "--output", default="Duong_Van_Giang_CV.pdf")
    ap.add_argument("--no-photo", action="store_true")
    args = ap.parse_args()
    build((ROOT / args.output).resolve(), with_photo=not args.no_photo)


if __name__ == "__main__":
    main()
