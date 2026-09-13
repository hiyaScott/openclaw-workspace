#!/usr/bin/env python3
"""
Z-Stair-Robot 场景合成图 - Pillow手动合成版 (v2)
改进: 中文字体、发光效果、更好的排版
"""

import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

# 配置
STAIRS_PHOTO = "/root/.openclaw/media/inbound/c4f0050d-dcee-41ef-b52c-233f03d135c7.jpg"
OUTPUT_DIR = "/root/.openclaw/workspace/projects/z-stair-robot/scene-composites"
os.makedirs(OUTPUT_DIR, exist_ok=True)

# 加载字体
FONT_BOLD = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
FONT_REG = "/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc"

try:
    font_title = ImageFont.truetype(FONT_BOLD, 22)
    font_label = ImageFont.truetype(FONT_BOLD, 16)
    font_body = ImageFont.truetype(FONT_REG, 14)
    font_small = ImageFont.truetype(FONT_REG, 12)
except:
    font_title = font_label = font_body = font_small = ImageFont.load_default()

# 加载楼梯照片
img = Image.open(STAIRS_PHOTO)
print(f"原图尺寸: {img.size}")

if img.width > 1600:
    ratio = 1600 / img.width
    img = img.resize((1600, int(img.height * ratio)), Image.LANCZOS)
    print(f"缩放后: {img.size}")

def draw_glow_line(draw, xy, fill, width, glow_radius=8, glow_color=None):
    """绘制带发光效果的线条"""
    if glow_color is None:
        glow_color = fill
    # 发光层
    for r in range(glow_radius, 0, -2):
        alpha = int(30 * (r / glow_radius))
        glow_fill = (*glow_color[:3], alpha)
        draw.line(xy, fill=glow_fill, width=width + r*2)
    # 主体线条
    draw.line(xy, fill=fill, width=width)

def draw_glow_rect(draw, coords, fill, outline, width, glow_radius=10):
    """绘制带发光效果的矩形"""
    for r in range(glow_radius, 0, -2):
        alpha = int(25 * (r / glow_radius))
        glow_outline = (*outline[:3], alpha)
        draw.rectangle(
            [coords[0]-r, coords[1]-r, coords[2]+r, coords[3]+r],
            outline=glow_outline, width=2
        )
    draw.rectangle(coords, fill=fill, outline=outline, width=width)

def add_text_with_bg(draw, text, pos, font, text_color=(255,255,255), bg_color=(0,0,0,160), padding=4):
    """在文字后添加半透明背景"""
    bbox = draw.textbbox((0,0), text, font=font)
    tw, th = bbox[2]-bbox[0], bbox[3]-bbox[1]
    x, y = pos
    # 背景
    draw.rectangle([x-padding, y-padding, x+tw+padding, y+th+padding], fill=bg_color)
    # 文字
    draw.text(pos, text, fill=text_color, font=font)

def create_scene(img, mode="climbing", output_name="scene.png"):
    canvas = img.copy().convert("RGBA")
    draw = ImageDraw.Draw(canvas)
    w, h = canvas.size
    
    # 顶部信息栏背景
    draw.rectangle([0, 0, w, 45], fill=(0, 0, 0, 180))
    
    if mode == "climbing":
        # ========== 楼梯攀爬模式 (90°) ==========
        draw.text((15, 12), "Z-Stair-Robot | 楼梯攀爬模式 (90°)", fill=(255, 255, 255), font=font_title)
        
        # 机器人位置 - 基于楼梯透视
        # 后脚垫（下层台阶）
        back_x1, back_y1 = int(w*0.55), int(h*0.60)
        back_x2, back_y2 = int(w*0.73), int(h*0.635)
        
        # 前脚垫（上层台阶）
        front_x1, front_y1 = int(w*0.55), int(h*0.35)
        front_x2, front_y2 = int(w*0.73), int(h*0.375)
        
        # 连杆位置
        link_left_top = (front_x1 + 15, front_y2)
        link_left_bottom = (back_x1 + 15, back_y1)
        link_right_top = (front_x2 - 15, front_y2)
        link_right_bottom = (back_x2 - 15, back_y1)
        
        # 发光效果参数
        RED = (220, 60, 60)
        GRAY = (70, 75, 85)
        WHITE = (255, 255, 255)
        
        # 绘制后脚垫
        draw_glow_rect(draw, [back_x1, back_y1, back_x2, back_y2],
                       fill=(*GRAY, 160), outline=(*WHITE, 200), width=2)
        # 前脚垫
        draw_glow_rect(draw, [front_x1, front_y1, front_x2, front_y2],
                       fill=(*GRAY, 160), outline=(*WHITE, 200), width=2)
        
        # 绘制连杆（带发光）
        draw_glow_line(draw, [link_left_bottom, link_left_top], (*RED, 230), 5, glow_radius=8)
        draw_glow_line(draw, [link_right_bottom, link_right_top], (*RED, 230), 5, glow_radius=8)
        
        # 关节（白色发光圆点）
        for pt in [link_left_top, link_left_bottom, link_right_top, link_right_bottom]:
            for r in range(6, 0, -1):
                alpha = int(40 * (r/6))
                draw.ellipse([pt[0]-r, pt[1]-r, pt[0]+r, pt[1]+r], fill=(*WHITE, alpha))
            draw.ellipse([pt[0]-3, pt[1]-3, pt[0]+3, pt[1]+3], fill=(*WHITE, 255), outline=(*RED, 255), width=1)
        
        # 标注
        add_text_with_bg(draw, "后脚垫 (锚定)", (back_x2 + 10, back_y1 + 5), font_label, text_color=(100, 255, 150))
        add_text_with_bg(draw, "前脚垫 (悬空/待着陆)", (front_x2 + 10, front_y1 + 5), font_label, text_color=(255, 200, 100))
        add_text_with_bg(draw, "双连杆", (link_left_top[0] - 50, (link_left_top[1] + link_left_bottom[1])//2 - 8), font_label, text_color=RED)
        
        # 尺寸标注线
        draw.line([(back_x1, back_y2 + 15), (back_x2, back_y2 + 15)], fill=(255, 255, 255, 150), width=1)
        draw.text(((back_x1+back_x2)//2 - 25, back_y2 + 18), "160mm", fill=(200, 200, 200), font=font_small)
        
        # 底部信息
        draw.rectangle([0, h-35, w, h], fill=(0, 0, 0, 180))
        draw.text((15, h-28), "脚垫: 160×45mm | 连杆行程: 20-60cm | 旋转: 0°→90° | 目标重量: <3kg", fill=(180, 180, 180), font=font_small)
        
    elif mode == "floor":
        # ========== 平地模式 (0°) ==========
        draw.text((15, 12), "Z-Stair-Robot | 平地模式 (0°)", fill=(255, 255, 255), font=font_title)
        
        # 在楼梯底部平台
        pad_y = int(h * 0.78)
        pad_left = int(w * 0.12)
        pad_right = int(w * 0.78)
        pad_h = 28
        
        GRAY = (70, 75, 85)
        RED = (220, 60, 60)
        
        # 展开的长底盘
        draw_glow_rect(draw, [pad_left, pad_y, pad_right, pad_y + pad_h],
                       fill=(*GRAY, 160), outline=(255, 255, 255, 200), width=2)
        
        # 中间拼接缝
        mid_x = (pad_left + pad_right) // 2
        draw.line([(mid_x, pad_y), (mid_x, pad_y + pad_h)], fill=(180, 180, 190, 180), width=2)
        
        # 连杆（收缩水平）
        link_y1 = pad_y - 6
        link_y2 = pad_y - 14
        draw_glow_line(draw, [(pad_left + 30, link_y1), (pad_right - 30, link_y1)], (*RED, 220), 4, glow_radius=6)
        draw_glow_line(draw, [(pad_left + 30, link_y2), (pad_right - 30, link_y2)], (*RED, 220), 4, glow_radius=6)
        
        # 标注
        add_text_with_bg(draw, "前脚垫", (pad_left + 10, pad_y + pad_h + 8), font_label)
        add_text_with_bg(draw, "后脚垫", (pad_right - 60, pad_y + pad_h + 8), font_label)
        add_text_with_bg(draw, "拼接缝", (mid_x - 20, pad_y + pad_h + 8), font_label, text_color=(180, 180, 180))
        add_text_with_bg(draw, "连杆收缩最短", (pad_left + 30, link_y2 - 22), font_label, text_color=RED)
        
        # 底部信息
        draw.rectangle([0, h-35, w, h], fill=(0, 0, 0, 180))
        draw.text((15, h-28), "连杆0°水平 | 关节滑至内侧 | 底盘连续覆盖 | 普通扫地机模式", fill=(180, 180, 180), font=font_small)
        
    elif mode == "sequence":
        # ========== 攀爬序列 ==========
        draw.text((15, 12), "Z-Stair-Robot | 尺蠖式攀爬序列", fill=(255, 255, 255), font=font_title)
        
        # 右侧信息面板
        panel_x, panel_y = w - 260, 60
        panel_w, panel_h = 240, 340
        draw.rectangle([panel_x, panel_y, panel_x + panel_w, panel_y + panel_h], fill=(0, 0, 0, 170), outline=(100, 100, 110, 150), width=1)
        
        draw.text((panel_x + 15, panel_y + 15), "攀爬四步法", fill=(255, 255, 255), font=font_label)
        
        steps = [
            ("① 锚定", "后脚垫真空吸盘吸附\n下层台阶，建立锚点", (100, 255, 150)),
            ("② 伸长", "双连杆同步伸展\n将前脚垫送上上层台阶", (100, 200, 255)),
            ("③ 着陆", "前脚垫吸盘锁定\n成为新的锚点", (255, 200, 100)),
            ("④ 回收", "后脚垫松开吸盘\n连杆收缩跟上，循环", (255, 150, 150)),
        ]
        
        for i, (title, desc, color) in enumerate(steps):
            y = panel_y + 55 + i * 70
            # 色块标识
            draw.ellipse([panel_x + 15, y, panel_x + 35, y + 20], fill=(*color, 200))
            draw.text((panel_x + 22, y + 3), str(i+1), fill=(0, 0, 0), font=font_label)
            # 标题和描述
            draw.text((panel_x + 45, y), title, fill=color, font=font_label)
            for j, line in enumerate(desc.split('\n')):
                draw.text((panel_x + 45, y + 20 + j*16), line, fill=(200, 200, 200), font=font_small)
        
        # 底部说明
        draw.rectangle([0, h-35, w, h], fill=(0, 0, 0, 180))
        draw.text((15, h-28), "类似尺蠖(毛毛虫)运动原理: 一节固定，一节移动，交替推进", fill=(180, 180, 180), font=font_small)
    
    # 保存
    output_path = os.path.join(OUTPUT_DIR, output_name)
    if canvas.mode == 'RGBA':
        background = Image.new('RGB', canvas.size, (30, 30, 35))
        background.paste(canvas, mask=canvas.split()[3])
        canvas = background
    canvas.save(output_path, quality=92)
    size_kb = os.path.getsize(output_path) // 1024
    print(f"✅ 已保存: {output_name} ({size_kb}KB)")
    return output_path


print("\n生成场景合成图 v2...")
print("-" * 40)

create_scene(img, "climbing", "scene-climbing-mode.png")
create_scene(img, "floor", "scene-floor-mode.png")
create_scene(img, "sequence", "scene-climbing-sequence.png")

print("-" * 40)
print(f"\n输出目录: {OUTPUT_DIR}")
for f in sorted(os.listdir(OUTPUT_DIR)):
    fpath = os.path.join(OUTPUT_DIR, f)
    if os.path.isfile(fpath) and f.endswith('.png'):
        print(f"  - {f} ({os.path.getsize(fpath)//1024}KB)")
