#!/usr/bin/env python3
"""
Z-Stair-Robot 场景合成图 - Pillow手动合成版
在真实楼梯照片上绘制机器人简化轮廓，做尺寸比例验证
"""

import os
from PIL import Image, ImageDraw, ImageFont

# 配置
STAIRS_PHOTO = "/root/.openclaw/media/inbound/c4f0050d-dcee-41ef-b52c-233f03d135c7.jpg"
OUTPUT_DIR = "/root/.openclaw/workspace/projects/z-stair-robot/scene-composites"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载楼梯照片
img = Image.open(STAIRS_PHOTO)
print(f"原图尺寸: {img.size}")

# 为了便于绘制，先把图片缩放到合理大小（保持比例）
MAX_WIDTH = 1600
if img.width > MAX_WIDTH:
    ratio = MAX_WIDTH / img.width
    new_size = (MAX_WIDTH, int(img.height * ratio))
    img = img.resize(new_size, Image.LANCZOS)
    print(f"缩放后: {img.size}")

def create_scene(img, mode="climbing", output_name="scene.png"):
    """
    mode: "climbing" 楼梯攀爬模式 | "floor" 平地模式 | "sequence" 运动序列
    """
    canvas = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    
    # 尝试加载字体
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 20)
        font_small = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 14)
    except:
        font = ImageFont.load_default()
        font_small = font
    
    if mode == "climbing":
        # ========== 楼梯攀爬模式 ==========
        # 在照片右下角区域绘制机器人（Z字形）
        # 基于照片中的台阶透视关系估算位置
        
        # 下层台阶（后脚垫位置）- 照片偏右下
        back_pad = [(w*0.55, h*0.62), (w*0.72, h*0.65)]  # 脚垫轮廓
        
        # 上层台阶（前脚垫位置）
        front_pad = [(w*0.55, h*0.38), (w*0.72, h*0.41)]
        
        # 连杆位置（左右两根）
        left_link = [(w*0.58, h*0.62), (w*0.58, h*0.38)]
        right_link = [(w*0.69, h*0.65), (w*0.69, h*0.41)]
        
        # 绘制后脚垫（深灰色填充+描边）
        draw.polygon([
            (back_pad[0][0], back_pad[0][1]),
            (back_pad[1][0], back_pad[0][1]),
            (back_pad[1][0], back_pad[1][1]),
            (back_pad[0][0], back_pad[1][1])
        ], fill=(60, 60, 70, 180), outline=(200, 200, 210, 255), width=2)
        
        # 绘制前脚垫
        draw.polygon([
            (front_pad[0][0], front_pad[0][1]),
            (front_pad[1][0], front_pad[0][1]),
            (front_pad[1][0], front_pad[1][1]),
            (front_pad[0][0], front_pad[1][1])
        ], fill=(60, 60, 70, 180), outline=(200, 200, 210, 255), width=2)
        
        # 绘制连杆（红色）
        draw.line(left_link, fill=(200, 50, 50, 220), width=6)
        draw.line(right_link, fill=(200, 50, 50, 220), width=6)
        
        # 绘制关节（白色圆点）
        for pt in [left_link[0], left_link[1], right_link[0], right_link[1]]:
            r = 5
            draw.ellipse([pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r], fill=(255, 255, 255, 200), outline=(200, 50, 50, 255), width=2)
        
        # 标注文字
        draw.text((w*0.73, h*0.63), "后脚垫", fill=(255, 255, 255, 255), font=font_small)
        draw.text((w*0.73, h*0.39), "前脚垫", fill=(255, 255, 255, 255), font=font_small)
        draw.text((w*0.50, h*0.50), "连杆", fill=(255, 100, 100, 255), font=font_small)
        
        # 标题
        draw.text((20, 20), "Z-Stair-Robot | 楼梯攀爬模式 (90°)", fill=(255, 255, 255, 255), font=font)
        
        # 尺寸标注
        draw.text((20, h-60), "脚垫: 160×45mm | 连杆行程: 20-60cm | 目标重量: <3kg", fill=(200, 200, 200, 255), font=font_small)
        
    elif mode == "floor":
        # ========== 平地模式 ==========
        # 机器人展开成一块长板
        
        # 在楼梯底部平台区域
        pad_y = h * 0.75
        pad_left = w * 0.15
        pad_right = w * 0.75
        pad_height = 35  # 像素高度
        
        # 绘制展开后的长底盘
        draw.polygon([
            (pad_left, pad_y),
            (pad_right, pad_y),
            (pad_right, pad_y + pad_height),
            (pad_left, pad_y + pad_height)
        ], fill=(60, 60, 70, 180), outline=(200, 200, 210, 255), width=2)
        
        # 中间分割线（表示前后脚垫拼接处）
        mid_x = (pad_left + pad_right) / 2
        draw.line([(mid_x, pad_y), (mid_x, pad_y + pad_height)], fill=(150, 150, 160, 200), width=2)
        
        # 连杆（收缩状态，水平，在底盘上方）
        link_y = pad_y - 8
        draw.line([(pad_left + 20, link_y), (pad_right - 20, link_y)], fill=(200, 50, 50, 220), width=4)
        draw.line([(pad_left + 20, link_y - 10), (pad_right - 20, link_y - 10)], fill=(200, 50, 50, 220), width=4)
        
        # 标注
        draw.text((20, 20), "Z-Stair-Robot | 平地模式 (0°)", fill=(255, 255, 255, 255), font=font)
        draw.text((pad_left, pad_y + pad_height + 10), "前后脚垫对接成一体", fill=(200, 200, 200, 255), font=font_small)
        draw.text((20, h-60), "连杆收缩至最短 | 关节滑至内侧 | 底部扫刷连续覆盖", fill=(200, 200, 200, 255), font=font_small)
        
    elif mode == "sequence":
        # ========== 攀爬序列 ==========
        # 在照片上展示攀爬的4个关键步骤（简化示意）
        
        steps = [
            {"name": "① 锚定", "desc": "后脚垫吸附"},
            {"name": "② 伸长", "desc": "连杆伸展"},
            {"name": "③ 着陆", "desc": "前脚垫锁定"},
            {"name": "④ 回收", "desc": "后脚垫跟上"},
        ]
        
        # 在左侧区域画一个小型序列图
        box_x, box_y = 20, 80
        box_w, box_h = 200, 320
        
        # 背景框
        draw.rectangle([box_x, box_y, box_x + box_w, box_y + box_h], fill=(0, 0, 0, 150), outline=(255, 255, 255, 100), width=1)
        
        draw.text((box_x + 10, box_y + 10), "攀爬序列", fill=(255, 255, 255, 255), font=font)
        
        step_h = 70
        for i, step in enumerate(steps):
            y = box_y + 50 + i * step_h
            # 步骤编号背景
            draw.ellipse([box_x + 15, y, box_x + 35, y + 20], fill=(200, 50, 50, 200))
            draw.text((box_x + 21, y + 3), str(i+1), fill=(255, 255, 255, 255), font=font_small)
            # 步骤名称
            draw.text((box_x + 45, y), step["name"], fill=(255, 255, 255, 255), font=font_small)
            draw.text((box_x + 45, y + 18), step["desc"], fill=(180, 180, 180, 255), font=font_small)
        
        # 主标题
        draw.text((20, 20), "Z-Stair-Robot | 尺蠖式攀爬原理", fill=(255, 255, 255, 255), font=font)
        draw.text((20, h-40), "类似尺蠖运动: 一脚固定 → 推杆伸长送另一脚 → 交换重复", fill=(200, 200, 200, 255), font=font_small)
    
    # 保存
    output_path = os.path.join(OUTPUT_DIR, output_name)
    # 转回RGB保存
    if canvas.mode == 'RGBA':
        background = Image.new('RGB', canvas.size, (0, 0, 0))
        background.paste(canvas, mask=canvas.split()[3])
        canvas = background
    canvas.save(output_path, quality=90)
    print(f"✅ 已保存: {output_path} ({os.path.getsize(output_path)//1024}KB)")
    return output_path


# 生成3张场景图
print("\n生成场景合成图...")
print("-" * 40)

create_scene(img, "climbing", "scene-climbing-mode.png")
create_scene(img, "floor", "scene-floor-mode.png")
create_scene(img, "sequence", "scene-climbing-sequence.png")

print("-" * 40)
print(f"\n全部完成！输出目录: {OUTPUT_DIR}")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, f)
    if os.path.isfile(fpath):
        print(f"  - {f} ({os.path.getsize(fpath)//1024}KB)")
