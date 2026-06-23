# CV / Portfolio — Fullstack Developer

CV cá nhân dạng **website + PDF**, viết bằng HTML · CSS · JS thuần (không build, không framework).
Màu chủ đạo teal/VETC, có dark mode, animation và bản in PDF sạch để gửi HR.

```
index.html    → nội dung CV (sửa text & placeholder ở đây)
styles.css    → giao diện + theme sáng/tối + style in PDF (@media print)
script.js     → dark mode, animation, đổ skill bar, đếm số, in PDF
```

## 1. Xem thử trên máy
Mở thẳng `index.html` bằng trình duyệt là chạy được (không cần server).
Hoặc chạy server tĩnh cho mượt:

```powershell
# Python
python -m http.server 5500
# rồi mở http://localhost:5500
```

## 2. Điền thông tin cá nhân
Mở `index.html`, tìm (Ctrl+F) chữ **`data-fill`** — đó là tất cả chỗ cần thay:
họ tên, email, SĐT, địa chỉ, GitHub, mốc thời gian công ty, trường học, năm tốt nghiệp…
Số liệu ở Hero (năm KN, số dự án) sửa ở thuộc tính `data-count`.

## 3. Xuất PDF gửi sếp / HR (khuyến nghị: dùng tool Python)
Xuất bằng `gen_pdf.py` cho layout gọn, lề & khoảng cách đều — ổn định hơn Ctrl+P.

```powershell
# Cài 1 lần
pip install -r requirements.txt
python -m playwright install chromium

# Xuất PDF
python gen_pdf.py                 # -> Duong_Van_Giang_CV.pdf
python gen_pdf.py -o cv.pdf       # đổi tên file
python gen_pdf.py --scale 0.95    # ép vào ít trang hơn nếu cần
```

Tool tự render `index.html` ở chế độ in (A4, lề 10–11mm) và **tự điền số điện thoại
thật** vào bản PDF (bản web vẫn ẩn sau captcha chống bot).

> Cách thủ công (không khuyến nghị): mở web → `Ctrl+P` → khổ A4, bật *Background graphics*.

## 4. Deploy lên Cloudflare Pages + domain Namecheap
1. Đẩy thư mục này lên 1 repo GitHub (hoặc dùng `wrangler`).
2. Cloudflare Dashboard → **Workers & Pages → Create → Pages** → kết nối repo.
   - Framework preset: **None**
   - Build command: *(để trống)*
   - Output directory: `/`
3. Sau khi deploy, vào **Custom domains** → thêm domain mua ở Namecheap.
4. Ở Namecheap, trỏ **NS** về Cloudflare (hoặc thêm bản ghi `CNAME` theo hướng dẫn Cloudflare).

> Cách nhanh nhất nếu chỉ có vài file tĩnh: kéo-thả thư mục vào **Cloudflare Pages → Direct Upload**.
```

