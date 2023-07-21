import random
from PIL import Image, ImageDraw
import numpy as np
import string

def get_nearest_color(colors, target_color):
    min_distance = float('inf')
    nearest_color = None
    for color in colors:
        distance = np.linalg.norm(np.array(color) - np.array(target_color))
        if distance < min_distance:
            min_distance = distance
            nearest_color = color
    return nearest_color

def merge_similar_colors(colors):
    merged_colors = []
    while colors:
        color = colors.pop(0)
        similar_colors = [color]
        for other_color in colors[:]:
            distance = np.linalg.norm(np.array(color) - np.array(other_color))
            if distance < 0.15:
                similar_colors.append(other_color)
                colors.remove(other_color)
        merged_color = tuple(np.mean(np.array(similar_colors), axis=0, dtype=int))
        merged_colors.append(merged_color)
    return merged_colors

def create_color_palette(color_data):
    colors = []
    appearance_ratios = []
    for data in color_data:
        hex_color, appearance_ratio = data
        # Xử lý mã hex có hoặc không có dấu "#"
        hex_color = hex_color.lstrip("#")
        # Kiểm tra mã hex có hợp lệ hay không
        if all(c in string.hexdigits for c in hex_color) and len(hex_color) == 6:
            # Chuyển đổi mã hex thành màu sắc
            color = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
            colors.append(color)
            appearance_ratios.append(appearance_ratio)
        else:
            print(f"Warning: Mã hex '{hex_color}' không hợp lệ. Bỏ qua màu sắc này.")
    return colors, appearance_ratios

def draw_random_colors(image, width, height, colors, appearance_ratios, pixel_size):
    draw = ImageDraw.Draw(image)
    for x in range(0, width, pixel_size):
        for y in range(0, height, pixel_size):
            color = random.choices(colors, weights=appearance_ratios)[0]
            draw.rectangle([(x, y), (x + pixel_size, y + pixel_size)], fill=color)
    return image

def assign_similar_colors(image, colors, pixel_size, similarity_ratio):
    width, height = image.size
    new_image = Image.new("RGB", (width, height))
    draw = ImageDraw.Draw(new_image)

    for x in range(0, width, pixel_size):
        for y in range(0, height, pixel_size):
            region = image.crop((x, y, x + pixel_size, y + pixel_size))
            region_colors = region.getcolors(pixel_size * pixel_size)
            if region_colors:
                dominant_color = max(region_colors, key=lambda x: x[0])[1]
                similar_color = get_nearest_color(colors, dominant_color)

                for i in range(pixel_size):
                    for j in range(pixel_size):
                        draw.point((x + i, y + j), fill=similar_color)

    return new_image

def main():
    user_width = int(input("Nhập chiều rộng của khung trống (px): "))
    user_height = int(input("Nhập chiều cao của khung trống (px): "))
    
    color_data = []
    while True:
        hex_color = input("Nhập mã hex của màu sắc (hoặc Enter để kết thúc): ")
        if not hex_color:
            break
        appearance_ratio = float(input("Nhập tỷ lệ xuất hiện màu sắc (từ 0 đến 1): "))
        color_data.append((hex_color, appearance_ratio))

    pixel_size = int(input("Nhập kích thước điểm ảnh (px): "))
    similarity_ratio = float(input("Nhập tỷ lệ gán màu tương tự (từ 0 đến 1): "))

    colors, appearance_ratios = create_color_palette(color_data)

    image = Image.new("RGB", (user_width, user_height), color="black") # tạo ra một khung trống 
    image_with_random_colors = draw_random_colors(image.copy(), user_width, user_height, colors, appearance_ratios, pixel_size) # điền màu vào khung

    final_image = assign_similar_colors(image_with_random_colors, colors, pixel_size, similarity_ratio)

    final_image.show()
    final_image.save('camofinal.png')

if __name__ == "__main__":
    main()
# lưu ý khi đặt màu sắc, tuyệt đối không sử dụng màu sắc từ ảnh, pick màu từ ảnh, nếu muốn pick phải đảm bảo ảnh chụp trong điều kiện ánh sáng tiêu chuẩn. Để đảm bảo chính xác hãy pick màu từ
# bảng màu hoặc pick màu online, ảnh chụp bị nhiễm sáng làm sai lệch kết quả thu nhận màu của code đọc màu, kết quả làm ảnh hưởng đến thuật toán điền màu khiến cho cả bức ảnh bị ám trắng hoặc các màu sắc khác