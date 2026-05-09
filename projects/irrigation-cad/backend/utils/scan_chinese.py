#!/usr/bin/env python3
"""
DWG 文件终极中文文本扫描器

DWG 2018+ 格式中，用户数据（图层名、文字等）可能以
多种编码存储。本脚本尝试所有可能的编码方式提取中文。
"""

import sys
import struct

def scan_utf16(data: bytes, byteorder: str = 'le') -> list:
    """扫描UTF-16编码的字符串"""
    texts = []
    i = 0
    while i < len(data) - 2:
        if byteorder == 'le':
            char = struct.unpack('<H', data[i:i+2])[0]
        else:
            char = struct.unpack('>H', data[i:i+2])[0]
        
        # 中文字符范围：0x4E00-0x9FFF（CJK统一表意文字）
        if 0x4E00 <= char <= 0x9FFF:
            start = i
            text_chars = [char]
            i += 2
            while i < len(data) - 1:
                if byteorder == 'le':
                    c = struct.unpack('<H', data[i:i+2])[0]
                else:
                    c = struct.unpack('>H', data[i:i+2])[0]
                if 0x4E00 <= c <= 0x9FFF or (0x0000 <= c <= 0x007F and c != 0):
                    text_chars.append(c)
                    i += 2
                else:
                    break
            
            if len(text_chars) >= 2:
                try:
                    text = ''.join(chr(c) for c in text_chars)
                    texts.append(text)
                except:
                    pass
        i += 1
    return texts

def scan_utf8(data: bytes) -> list:
    """扫描UTF-8编码的中文字符串"""
    texts = []
    i = 0
    while i < len(data) - 2:
        # UTF-8 中文字符：3字节，首字节 0xE4-0xEF
        if 0xE4 <= data[i] <= 0xEF:
            start = i
            text_bytes = bytearray()
            while i < len(data) - 2:
                if 0xE4 <= data[i] <= 0xEF and data[i+1] >= 0x80 and data[i+2] >= 0x80:
                    text_bytes.extend(data[i:i+3])
                    i += 3
                else:
                    break
            
            if len(text_bytes) >= 6:  # 至少2个中文字符
                try:
                    text = text_bytes.decode('utf-8')
                    texts.append(text)
                except:
                    pass
        i += 1
    return texts

def scan_gbk(data: bytes) -> list:
    """扫描GBK编码的中文字符串"""
    texts = []
    i = 0
    while i < len(data) - 1:
        # GBK 中文字符：首字节 0xB0-0xF7
        if 0xB0 <= data[i] <= 0xF7 and 0xA1 <= data[i+1] <= 0xFE:
            start = i
            text_bytes = bytearray()
            while i < len(data) - 1:
                if 0xB0 <= data[i] <= 0xF7 and 0xA1 <= data[i+1] <= 0xFE:
                    text_bytes.extend(data[i:i+2])
                    i += 2
                else:
                    break
            
            if len(text_bytes) >= 4:
                try:
                    text = text_bytes.decode('gbk')
                    texts.append(text)
                except:
                    pass
        i += 1
    return texts

def main(filepath):
    with open(filepath, 'rb') as f:
        data = f.read()
    
    print(f"文件: {filepath}")
    print(f"大小: {len(data):,} bytes")
    print()
    
    # UTF-8
    print("=== UTF-8 中文字符串 ===")
    utf8_texts = scan_utf8(data)
    unique_utf8 = list(set(utf8_texts))
    print(f"找到 {len(unique_utf8)} 个唯一字符串:")
    for text in sorted(unique_utf8, key=len, reverse=True)[:50]:
        print(f"  [{text}]")
    print()
    
    # UTF-16 LE
    print("=== UTF-16 LE 中文字符串 ===")
    utf16le_texts = scan_utf16(data, 'le')
    unique_utf16le = list(set(utf16le_texts))
    print(f"找到 {len(unique_utf16le)} 个唯一字符串:")
    for text in sorted(unique_utf16le, key=len, reverse=True)[:50]:
        print(f"  [{text}]")
    print()
    
    # UTF-16 BE
    print("=== UTF-16 BE 中文字符串 ===")
    utf16be_texts = scan_utf16(data, 'be')
    unique_utf16be = list(set(utf16be_texts))
    print(f"找到 {len(unique_utf16be)} 个唯一字符串:")
    for text in sorted(unique_utf16be, key=len, reverse=True)[:50]:
        print(f"  [{text}]")
    print()
    
    # GBK
    print("=== GBK 中文字符串 ===")
    gbk_texts = scan_gbk(data)
    unique_gbk = list(set(gbk_texts))
    print(f"找到 {len(unique_gbk)} 个唯一字符串:")
    for text in sorted(unique_gbk, key=len, reverse=True)[:50]:
        print(f"  [{text}]")
    print()
    
    # 合并所有结果
    all_texts = set(unique_utf8 + unique_utf16le + unique_utf16be + unique_gbk)
    print(f"=== 总计: {len(all_texts)} 个唯一中文字符串 ===")
    for text in sorted(all_texts, key=len, reverse=True)[:100]:
        print(f"  {text}")

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 scan_chinese.py <dwg_file>")
        sys.exit(1)
    main(sys.argv[1])
