import os
from PIL import Image

# 输入 / 输出路径
input_dir = "/root/roadscene2vec/examples/images"
output_dir = "/root/roadscene2vec/examples/images/raw_images"

# 创建输出目录
os.makedirs(output_dir, exist_ok=True)

# 支持的图片格式
IMG_EXTENSIONS = (".png", ".jpg", ".jpeg", ".bmp")

for filename in os.listdir(input_dir):
    if not filename.lower().endswith(IMG_EXTENSIONS):
        continue

    input_path = os.path.join(input_dir, filename)

    try:
        img = Image.open(input_path)
        width, height = img.size

        # 👉 四个视野上下拼接 → 每个占 1/4 高度
        top_crop = img.crop((0, 0, width, height // 4))

        # 👉 加前缀
        new_name = filename
        output_path = os.path.join(output_dir, new_name)

        # 保存
        top_crop.save(output_path)

        print(f"Saved: {output_path}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")

# 路径
input_dir = "/root/roadscene2vec/examples/images/raw_images"
ref_image_path = "/root/roadscene2vec/examples/images/front/raw_images/00097114.jpg"

# 👉 读取参考尺寸
ref_img = Image.open(ref_image_path)
target_size = ref_img.size  # (width, height)

print("Target size:", target_size)

# 获取所有图片
files = sorted([
    f for f in os.listdir(input_dir)
    if f.lower().endswith((".jpg", ".png", ".jpeg"))
])

# 👉 起始编号
start_index = 97097

# ⚠️ 防止覆盖：先加 tmp 前缀
for f in files:
    old_path = os.path.join(input_dir, f)
    tmp_path = os.path.join(input_dir, "tmp_" + f)
    os.rename(old_path, tmp_path)

# 重新获取文件列表
files = sorted(os.listdir(input_dir))

# 👉 处理：resize + 重命名
for i, filename in enumerate(files):
    if not filename.startswith("tmp_"):
        continue

    old_path = os.path.join(input_dir, filename)

    try:
        img = Image.open(old_path)

        # 👉 resize
        img_resized = img.resize(target_size, Image.BILINEAR)

        # 👉 新文件名
        new_name = f"{start_index + i:08d}.jpg"
        new_path = os.path.join(input_dir, new_name)

        # 保存
        img_resized.save(new_path)

        # 删除旧文件
        os.remove(old_path)

        print(f"{filename} -> {new_name}")

    except Exception as e:
        print(f"Error processing {filename}: {e}")