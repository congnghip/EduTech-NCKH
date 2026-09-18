# MOOCCubeX Raw Data Explorer (`viewer/`)

Trình xem và khám phá dữ liệu thô chuyên dụng cho kho dữ liệu **MOOCCubeX** (`data_raw/`, ~44 GB).

---

## 🌟 Tính năng chính

- **Tập trung 100% vào dữ liệu thô**: Không còn các biểu đồ giả định, timeline hay slide lý thuyết.
- **Hỗ trợ toàn bộ 33 file trong `data_raw/`**:
  - 📦 **Entities (11 files)**: `course.json`, `problem.json`, `user.json`, `video.json`, `comment.json`, `reply.json`, `teacher.json`, `school.json`, `concept.json`, `paper.json`, `other.json`.
  - 🔗 **Relations & Logs (18 files)**: `user-problem.json` (22.5 GB), `user-video.json` (3.18 GB), `exercise-problem.txt`, `course-teacher.txt`, `course-school.txt`, `course-field.json`, `video_id-ccid.txt`, `user-comment.txt`, v.v.
  - 🧠 **Prerequisites (3 files)**: `cs.json`, `math.json`, `psy.json`.
- **4 Chế độ xem linh hoạt**:
  1. 📋 **Bảng dữ liệu (Table View)**: Tự động trích xuất các cột thuộc tính, định dạng số, ID, Boolean và mảng lồng nhau.
  2. 📄 **Dòng thô (Raw Lines / JSON View)**: Hiển thị từng dòng bản ghi gốc kèm số dòng và nút copy 1-click.
  3. 🔍 **Cấu trúc trường (Schema View)**: Thống kê tên trường, kiểu dữ liệu (Types), tỷ lệ khuyết (Nulls) và giá trị mẫu.
  4. 📐 **Sơ đồ lớp (Class Diagram)**: Sơ đồ kiến trúc UML trực quan cho toàn bộ 14 lớp thực thể, nhật ký và quan hệ trong MOOCCubeX:
     - Thể hiện đầy đủ thuộc tính, khóa chính `[PK]`, khóa ngoại `[FK]`, kiểu dữ liệu và đường liên kết SVG (cardinality `1..*`).
     - Hỗ trợ **Pan & Zoom** mượt mà (kéo chuột, lăn chuột hoặc nút bấm).
     - Lọc theo nhóm: *Thực thể cốt lõi*, *Nhật ký tương tác (Logs 25GB+)*, *Quan hệ & Cầu nối*, *Tri thức & Tiên quyết*.
     - Nhấn nút **"Xem dữ liệu thô"** trên từng lớp UML để nhảy trực tiếp đến bảng dữ liệu thật của file đó!
     - Nút **"🎯 Tiêu điểm"** giúp định vị và tự động phóng to vào lớp của file đang mở.
- **Chi tiết bản ghi (Inspector Drawer)**: Bấm vào bất kỳ dòng nào để xem bảng thuộc tính chi tiết dạng Key-Value và JSON hoàn chỉnh.
- **Hiệu năng cực cao**:
  - Đọc file 22 GB chỉ mất **~2 ms** nhờ cơ chế stream / skip dòng theo yêu cầu (không load toàn bộ file vào RAM).
  - Tìm kiếm (Search) theo từ khóa hoặc ID thời gian thực.
  - Phân trang linh hoạt (25, 50, 100, 200 dòng/trang), nhảy nhanh đến dòng số bất kỳ.

---

## 🚀 Hướng dẫn khởi chạy

### Cách 1: Khởi chạy Data Server (Khuyên dùng - Xem toàn bộ 40GB+)

Chỉ cần Python 3 có sẵn trên máy (không cần cài thêm bất kỳ thư viện ngoài nào):

```bash
cd /home/congnghip/project/Data_NCKH/viewer
python3 server.py
```

Server sẽ tự động mở tại: **`http://localhost:8080`**

### Cách 2: Mở trực tiếp file HTML (Chế độ xem mẫu Offline)

Bạn có thể double-click mở trực tiếp file `index.html` trong trình duyệt web:

```bash
xdg-open /home/congnghip/project/Data_NCKH/viewer/index.html
```

*(Chế độ này hiển thị sẵn 30 dòng mẫu thực tế cho mỗi file thông qua `samples.js` mà không cần bật server).*
