"""
DWG 文件基础信息提取器

DWG是Autodesk专有格式，但可以读取文件头部和
一些基础元数据。完整的图形数据解析需要
ODA File Converter或AutoCAD引擎。
"""

import struct
import sys
from typing import Dict, List, Optional, Tuple


class DWGInfoExtractor:
    """提取DWG文件的基础信息"""
    
    # DWG版本标识符映射
    VERSION_MAP = {
        b'AC1012': 'R13',
        b'AC1014': 'R14',
        b'AC1015': '2000',
        b'AC1018': '2004',
        b'AC1021': '2007',
        b'AC1024': '2010',
        b'AC1027': '2013',
        b'AC1032': '2018/2019/2020/2021/2022',
    }
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.version_str = None
        self.file_size = 0
        self.header_info = {}
    
    def extract(self) -> Dict:
        """提取所有可用信息"""
        try:
            with open(self.filepath, 'rb') as f:
                self.file_size = len(f.read())
                f.seek(0)
                
                # 读取版本标识符（前6个字节）
                version_bytes = f.read(6)
                self.version_str = self.VERSION_MAP.get(version_bytes, 'Unknown')
                
                # 尝试读取更多头部信息
                self._read_header(f)
                
            return {
                'version_bytes': version_bytes.decode('ascii', errors='replace'),
                'version_name': self.version_str,
                'file_size': self.file_size,
                'file_size_mb': round(self.file_size / (1024 * 1024), 2),
                'header_info': self.header_info,
                'can_parse_full': False,  # 完整解析需要转换器
                'note': '完整图形数据解析需要DWG转DXF'
            }
            
        except Exception as e:
            return {
                'error': str(e),
                'version_name': 'Unknown',
                'file_size': self.file_size
            }
    
    def _read_header(self, f):
        """尝试读取DWG文件头信息（简化版）"""
        try:
            # 读取一些基础头部字段
            f.seek(0x0D)  # 跳过版本标识
            
            # 维护版本号
            maint_release = struct.unpack('<B', f.read(1))[0]
            
            # 图像搜索偏移量
            f.seek(0x15)
            image_offset = struct.unpack('<I', f.read(4))[0]
            
            # 图像大小
            image_size = struct.unpack('<I', f.read(4))[0]
            
            # 实体数量（近似值，位置随版本变化）
            f.seek(0x21)
            
            self.header_info = {
                'maint_release': maint_release,
                'image_offset': image_offset,
                'image_size': image_size,
                'has_preview': image_size > 0
            }
            
        except Exception as e:
            self.header_info = {'parse_error': str(e)}


def extract_text_chunks(filepath: str, min_length: int = 4) -> List[str]:
    """
    从DWG中提取可读的文本片段
    
    可以提取：图层名、块名、属性值、标注文字等
    """
    texts = []
    try:
        with open(filepath, 'rb') as f:
            data = f.read()
        
        # 寻找可打印的ASCII/UTF-8文本序列
        current = []
        for byte in data:
            if 32 <= byte <= 126 or byte in (0xC0, 0xC1, 0xC2, 0xC3):  # ASCII + UTF-8起始字节
                current.append(byte)
            else:
                if len(current) >= min_length:
                    try:
                        text = bytes(current).decode('utf-8', errors='replace')
                        if any(c.isalpha() for c in text):  # 至少包含字母
                            texts.append(text)
                    except:
                        pass
                current = []
        
        # 去重并过滤
        unique_texts = list(set(texts))
        # 过滤掉常见的无意义字符串
        filtered = [
            t for t in unique_texts 
            if len(t) >= min_length 
            and not all(c in '0123456789' for c in t)
            and not t.startswith(('ACDb', 'ACAD_', 'Dx', 'H@', 'HdA'))
        ]
        
        return sorted(filtered, key=len, reverse=True)[:200]  # 返回最长的200个
        
    except Exception as e:
        return [f"Error: {e}"]


def analyze_dwg(filepath: str) -> str:
    """
    完整的DWG分析报告
    """
    lines = []
    lines.append("=" * 60)
    lines.append("DWG 文件分析报告")
    lines.append("=" * 60)
    lines.append("")
    
    # 基础信息
    extractor = DWGInfoExtractor(filepath)
    info = extractor.extract()
    
    lines.append(f"文件: {filepath.split('/')[-1]}")
    lines.append(f"版本: {info.get('version_name', 'Unknown')} ({info.get('version_bytes', '')})")
    lines.append(f"大小: {info.get('file_size', 0):,} bytes ({info.get('file_size_mb', 0)} MB)")
    lines.append("")
    
    # 头部信息
    header = info.get('header_info', {})
    if 'parse_error' not in header:
        lines.append(f"维护版本: {header.get('maint_release', 'N/A')}")
        lines.append(f"预览图偏移: {header.get('image_offset', 'N/A')}")
        lines.append(f"预览图大小: {header.get('image_size', 'N/A')} bytes")
        lines.append(f"包含预览图: {'是' if header.get('has_preview') else '否'}")
        lines.append("")
    
    # 文本提取
    lines.append("-" * 60)
    lines.append("提取的文本片段（可能的图层名/属性值）")
    lines.append("-" * 60)
    
    texts = extract_text_chunks(filepath)
    
    # 分类显示
    potential_layers = []
    other_texts = []
    
    for text in texts[:100]:
        text_clean = text.strip()
        # 可能是图层名的特征
        if (len(text_clean) >= 3 and len(text_clean) <= 50
            and any(c.isalpha() for c in text_clean)
            and text_clean not in ('True', 'False', 'None', 'null')):
            potential_layers.append(text_clean)
        else:
            other_texts.append(text_clean)
    
    lines.append(f"\n可能的图层名/标识符（{len(potential_layers)}个）:")
    for i, text in enumerate(potential_layers[:30], 1):
        lines.append(f"  {i:2d}. {text}")
    
    if len(potential_layers) > 30:
        lines.append(f"  ... 还有 {len(potential_layers) - 30} 个")
    
    lines.append("")
    lines.append("=" * 60)
    lines.append("说明：完整图形数据解析需要将DWG转为DXF格式")
    lines.append("建议：使用 ODA File Converter 或 AutoCAD 进行转换")
    lines.append("=" * 60)
    
    return "\n".join(lines)


if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("用法: python3 dwg_analyzer.py <dwg_file_path>")
        sys.exit(1)
    
    filepath = sys.argv[1]
    report = analyze_dwg(filepath)
    print(report)
