from PIL import Image, ImageOps, ImageEnhance

def auto_adjust_image(img: Image.Image) -> Image.Image:
    """
    [ĐÃ VÔ HIỆU HÓA ĐỂ BẢO TOÀN TRUNG THỰC MÀU DA]
    Bất kỳ sự can thiệp nào vào độ sáng, tương phản hay bão hòa (saturation)
    đều làm thay đổi đặc tính Undertone và Hue của khuôn mặt, dẫn đến AI dự đoán sai.
    Hàm này giờ chỉ trả về nguyên bản.
    """
    return img

def process_face_image(img: Image.Image) -> Image.Image:
    """
    Hàm xử lý ảnh đầu vào:
    Vì bài toán Personal Color yêu cầu ĐỘ CHÍNH XÁC TUYỆT ĐỐI về màu sắc gốc, 
    ta sẽ KHÔNG tách nền (gây quầng viền giả) và KHÔNG chỉnh màu tự động.
    Ta chỉ dùng OpenCV crop khung hình gọn lại quanh khuôn mặt (để giao diện đẹp hơn)
    mà vẫn giữ đủ thông tin cho Face Parsing model phán đoán.
    """
    # Chuyển qua chuẩn RGB để phòng các case ảnh la
    img = img.convert("RGB")
    final_img = img.copy()

    # Nhận diện vị trí khuôn mặt bằng OpenCV để crop lại cho đẹp trên UI UI
    try:
        import cv2
        import numpy as np
        
        cv_img = np.array(final_img)
        # Convert RGB to BGR for cv2
        cv_img = cv_img[:, :, ::-1].copy()
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Load haar cascade mặc định của openCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=5, minSize=(100, 100))
        
        if len(faces) > 0:
            # Lấy khuôn mặt to nhất 
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = faces[0]
            
            # Mở rộng bounding box thật RỘNG để không che mất viền cổ, vai, tóc (Quan trọng cho FaRL model)
            pad_w = int(w * 0.8)
            pad_h_top = int(h * 0.8)
            pad_h_bot = int(h * 1.2) 
            
            x1 = max(0, x - pad_w)
            y1 = max(0, y - pad_h_top)
            x2 = min(cv_img.shape[1], x + w + pad_w)
            y2 = min(cv_img.shape[0], y + h + pad_h_bot)
            
            final_img = final_img.crop((x1, y1, x2, y2))
            
    except Exception as e:
        print(f"Lỗi crop mặt: {e}")
        pass
        
    return final_img

