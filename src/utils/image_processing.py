from PIL import Image, ImageOps, ImageEnhance

def auto_adjust_image(img: Image.Image) -> Image.Image:
    """
    Chuẩn hóa ánh sáng tự nhiên để phục vụ bài toán nhận diện màu da, undertone 
    và personal color một cách khách quan, chính xác và ổn định nhất.
    Không dùng bộ lọc làm đẹp, ưu tiên tính trung thực của màu da.
    """
    # 1. Tự động cân bằng lại dải sáng bằng autocontrast (giảm chênh lệch giữa vùng quá tối và vùng quá sáng)
    img = ImageOps.autocontrast(img, cutoff=1)
    
    # 2. Tăng nhẹ độ sáng khoảng +3% để ảnh sáng hơn nhưng vẫn giữ chi tiết thật của da
    enhancer_brightness = ImageEnhance.Brightness(img)
    img = enhancer_brightness.enhance(1.03)
    
    # 3. Tăng nhẹ độ tương phản khoảng +4% để tách tốt hơn giữa vùng sáng và bóng
    enhancer_contrast = ImageEnhance.Contrast(img)
    img = enhancer_contrast.enhance(1.04)
    
    # 4. Tăng rất nhẹ độ rực màu khoảng +4% để màu da không bị nhợt do ánh sáng tự nhiên, không làm sai lệch undertone
    enhancer_color = ImageEnhance.Color(img)
    img = enhancer_color.enhance(1.04)
    
    return img

def process_face_image(img: Image.Image) -> Image.Image:
    """
    Hàm xử lý ảnh đầu vào:
    1. Tách nền (giữ lại người) sử dụng rembg.
    2. Đổi phông nền chuẩn thành Trắng Tinh.
    3. Nhận diện vị trí khuôn mặt bằng OpenCV.
    4. Cắt chuẩn (Crop) bao trọn mặt và cổ, bỏ đi các vùng thừa thãi.
    """
    try:
        from rembg import remove
    except ImportError:
        # Nếu chưa cài rembg, fallback về việc chỉ điều chỉnh ánh sáng
        return auto_adjust_image(img)
        
    # Chuyển qua chuẩn RGB để phòng các case ảnh la
    img = img.convert("RGB")
    
    # 1. Tách nền bằng rembg -> Trả về RGBA
    img_rgba = remove(img)
    
    # 2. Thay bằng nền màu trắng tinh
    final_img = Image.new("RGB", img_rgba.size, (255, 255, 255))
    final_img.paste(img_rgba, mask=img_rgba.split()[3])

    # 3. Sử dụng OpenCV để Crop chính xác vào khuôn mặt
    try:
        import cv2
        import numpy as np
        
        cv_img = np.array(final_img)
        # Convert RGB to BGR for cv2
        cv_img = cv_img[:, :, ::-1].copy()
        gray = cv2.cvtColor(cv_img, cv2.COLOR_BGR2GRAY)
        
        # Load haar cascade mặc định của openCV
        face_cascade = cv2.CascadeClassifier(cv2.data.haarcascades + 'haarcascade_frontalface_default.xml')
        faces = face_cascade.detectMultiScale(gray, scaleFactor=1.1, minNeighbors=4, minSize=(50, 50))
        
        if len(faces) > 0:
            # Lấy khuôn mặt to nhất (hạn chế nhận diện nhầm)
            faces = sorted(faces, key=lambda x: x[2] * x[3], reverse=True)
            x, y, w, h = faces[0]
            
            # Mở rộng bounding box một chút để lấy cả đỉnh đầu, 2 bên tai và cổ
            pad_w = int(w * 0.45)
            pad_h_top = int(h * 0.5)
            pad_h_bot = int(h * 0.75) # lấy phần dưới nhiều hơn để bao trọn cổ
            
            x1 = max(0, x - pad_w)
            y1 = max(0, y - pad_h_top)
            x2 = min(cv_img.shape[1], x + w + pad_w)
            y2 = min(cv_img.shape[0], y + h + pad_h_bot)
            
            final_img = final_img.crop((x1, y1, x2, y2))
        else:
            # Fallback nếu ko tìm thấy mặt, crop theo bounding box của người
            bbox = img_rgba.getbbox()
            if bbox:
                final_img = final_img.crop(bbox)
    except Exception as e:
        # Fallback an toàn nếu OpenCV lỗi
        bbox = img_rgba.getbbox()
        if bbox:
            final_img = final_img.crop(bbox)
    
    # 5. Cân chỉnh sáng tự động
    final_img = auto_adjust_image(final_img)
    return final_img
