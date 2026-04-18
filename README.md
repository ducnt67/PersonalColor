# BeautyTone AI - Personal Color & Style Assistant

Đây là một ứng dụng AI/ML liên quan đến phân tích personal color/seasonal color analysis, được xây dựng dựa trên Streamlit và mô hình PyTorch. UI đã được tối ưu hóa đẹp mắt, sáng và chuyên nghiệp.

## Cấu trúc thư mục mới:
- `.streamlit/`: Cấu hình Streamlit (config.toml).
- `assets/`: Chứa file tài nguyên web như css, font, hình ảnh.
- `data/`: Chứa các dữ liệu dạng csv bao gồm profile và palette màu các mùa.
- `models/`: Chứa mô hình AI (`best_personal_color_model.pth`).
- `src/`: Mã nguồn của ứng dụng, được chia thành các helpers, pages, services, và ui classes.
- `app.py`: File chạy chính cho project.

## Hướng dẫn cài đặt và chạy ứng dụng

1. **Cài đặt thư viện:**
   Bạn cần có Python 3.8+ và cài đặt các thư viện yêu cầu:
   ```bash
   pip install -r requirements.txt
   ```

2. **Chạy ứng dụng:**
   ```bash
   streamlit run app.py
   ```
