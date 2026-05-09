"""
DWG 2018 深度二进制解析器

尝试从DWG 2018文件中提取更多的结构信息，
包括Section Map、Classes、以及可能未加密的对象数据。
"""

import struct
import zlib
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass 
class DWGPage:
    """DWG数据页"""
    offset: int
    size: int
    decompressed_size: int


@dataclass
class DWGSectionInfo:
    """DWG Section信息"""
    name: str
    seeker: int
    size: int
    page_count: int
    max_decomp_size: int
    pages: List[DWGPage]


class DWG2018DeepParser:
    """DWG 2018深度解析器"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.data: bytes = b''
        self.sections: List[DWGSectionInfo] = []
    
    def parse(self) -> Dict:
        """深度解析DWG文件"""
        result = {
            'version': None,
            'file_size': 0,
            'header_info': {},
            'sections': [],
            'potential_objects': [],
            'layer_references': [],
            'text_strings': [],
            'errors': []
        }
        
        try:
            with open(self.filepath, 'rb') as f:
                self.data = f.read()
            
            result['file_size'] = len(self.data)
            
            # 1. 验证版本
            version = self.data[0:6].decode('ascii')
            result['version'] = version
            
            # 2. 读取文件头
            header = self._parse_header()
            result['header_info'] = header
            
            # 3. 尝试找到并解析Section Map
            self._find_sections()
            result['sections'] = [
                {
                    'name': s.name,
                    'seeker': s.seeker,
                    'size': s.size,
                    'page_count': s.page_count,
                    'max_decomp_size': s.max_decomp_size
                }
                for s in self.sections
            ]
            
            # 4. 扫描可能的文本字符串
            texts = self._scan_text_strings()
            result['text_strings'] = texts[:100]
            
            # 5. 查找图层引用
            layers = self._find_layer_references()
            result['layer_references'] = layers
            
            # 6. 估算对象
            result['potential_objects'] = self._count_object_references()
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _parse_header(self) -> Dict:
        """解析DWG 2018文件头"""
        # DWG 2018 文件头结构 (0x00 - 0x100)
        data = self.data
        
        header = {
            'version': data[0:6].decode('ascii'),
            'maint_release': data[0x0D] if len(data) > 0x0D else 0,
            'codepage': struct.unpack('<H', data[0x0E:0x10])[0] if len(data) > 0x10 else 0,
            'number_of_sections': 0,
            'section_map_offset': 0,
            'section_map_size': 0,
        }
        
        # 0x20-0x23: VBA项目地址
        if len(data) >= 0x24:
            header['vba_address'] = struct.unpack('<I', data[0x20:0x24])[0]
        
        # 0x24-0x27: 未知
        if len(data) >= 0x28:
            header['unknown_24'] = struct.unpack('<I', data[0x24:0x28])[0]
        
        # Section Locator Records 从 0x80 开始
        # DWG 2018有固定数量的section locators
        
        return header
    
    def _find_sections(self):
        """在文件中查找section信息"""
        # 方法：搜索已知的DWG section名称签名
        # DWG 2018 section locator records 在文件头之后
        
        section_signatures = [
            (b'AcDb:FileDepList', 'FileDepList'),
            (b'AcDb:Preview', 'Preview'),
            (b'AcDb:SummaryInfo', 'SummaryInfo'),
            (b'AcDb:RevHistory', 'RevHistory'),
            (b'AcDb:AcDbObjects', 'AcDbObjects'),
            (b'AcDb:Classes', 'Classes'),
            (b'AcDb:Handles', 'Handles'),
            (b'AcDb:AuxHeader', 'AuxHeader'),
            (b'AcDb:Template', 'Template'),
            (b'AcDb:Prototype_1b', 'Prototype'),
        ]
        
        found = set()
        for sig, name in section_signatures:
            offset = 0
            while True:
                idx = self.data.find(sig, offset)
                if idx == -1 or idx in found:
                    break
                found.add(idx)
                
                # 尝试读取section大小
                size = 0
                if len(self.data) > idx + len(sig) + 4:
                    try:
                        size = struct.unpack('<I', self.data[idx+len(sig):idx+len(sig)+4])[0]
                    except:
                        pass
                
                self.sections.append(DWGSectionInfo(
                    name=name,
                    seeker=idx,
                    size=size,
                    page_count=0,
                    max_decomp_size=0,
                    pages=[]
                ))
                offset = idx + 1
    
    def _scan_text_strings(self) -> List[str]:
        """扫描文件中的文本字符串"""
        texts = []
        data = self.data
        
        # 扫描可能的UTF-8短字符串
        i = 0
        while i < len(data) - 3:
            # 寻找可打印字符序列
            if data[i] >= 0x20 and data[i] < 0x7F:
                # ASCII范围
                start = i
                while i < len(data) and data[i] >= 0x20 and data[i] < 0x7F:
                    i += 1
                length = i - start
                if length >= 3 and length <= 50:
                    text = data[start:i].decode('ascii', errors='replace')
                    # 过滤有意义的字符串
                    if any(c.isalpha() for c in text) and not text.startswith(('ACDb', 'HdA', 'L@S')):
                        texts.append(text)
            elif data[i] >= 0xC0 and data[i] <= 0xDF and i + 1 < len(data):
                # UTF-8双字节
                start = i
                while i < len(data) - 1:
                    if data[i] >= 0xC0 and data[i] <= 0xDF and data[i+1] >= 0x80 and data[i+1] <= 0xBF:
                        i += 2
                    elif data[i] >= 0xE0 and data[i] <= 0xEF and i + 2 < len(data) and data[i+1] >= 0x80 and data[i+2] >= 0x80:
                        i += 3
                    else:
                        break
                length = i - start
                if length >= 6:
                    try:
                        text = data[start:i].decode('utf-8', errors='replace')
                        if len(text) >= 2 and any('\u4e00' <= c <= '\u9fff' for c in text):
                            texts.append(text)
                    except:
                        pass
            i += 1
        
        # 去重
        return list(set(texts))
    
    def _find_layer_references(self) -> List[str]:
        """查找图层引用"""
        layers = []
        
        # DWG 2018中，LAYER对象的类名是 "AcDbLayerTableRecord"
        # 搜索这个特征
        layer_sig = b'AcDbLayerTableRecord'
        offset = 0
        while True:
            idx = self.data.find(layer_sig, offset)
            if idx == -1:
                break
            
            # 尝试在附近读取图层名
            # 图层名通常在对象签名后的几个字节
            name_start = idx + len(layer_sig) + 2
            if name_start < len(self.data):
                name_bytes = bytearray()
                i = name_start
                while i < len(self.data) and self.data[i] != 0 and len(name_bytes) < 50:
                    name_bytes.append(self.data[i])
                    i += 1
                try:
                    name = bytes(name_bytes).decode('utf-8', errors='replace').strip()
                    if len(name) > 0 and name != '\x00':
                        layers.append(name)
                except:
                    pass
            
            offset = idx + 1
        
        return list(set(layers))
    
    def _count_object_references(self) -> List[Dict]:
        """统计对象引用"""
        objects = []
        
        # 搜索常见的对象类型签名
        object_signatures = [
            (b'AcDbEntity', 'Entity'),
            (b'AcDbLine', 'Line'),
            (b'AcDbCircle', 'Circle'),
            (b'AcDbArc', 'Arc'),
            (b'AcDbPolyline', 'Polyline'),
            (b'AcDbLayerTable', 'LayerTable'),
            (b'AcDbBlockTable', 'BlockTable'),
            (b'AcDbText', 'Text'),
            (b'AcDbMText', 'MText'),
            (b'AcDbDimension', 'Dimension'),
            (b'AcDbHatch', 'Hatch'),
            (b'AcDbSpline', 'Spline'),
            (b'AcDbEllipse', 'Ellipse'),
        ]
        
        for sig, obj_type in object_signatures:
            count = self.data.count(sig)
            if count > 0:
                objects.append({'type': obj_type, 'count': count})
        
        return sorted(objects, key=lambda x: x['count'], reverse=True)
    
    def print_report(self, result: Dict):
        """打印详细报告"""
        print("=" * 60)
        print(f"DWG 深度解析报告")
        print("=" * 60)
        print()
        
        print(f"文件版本: {result.get('version', 'Unknown')}")
        print(f"文件大小: {result.get('file_size', 0):,} bytes")
        print()
        
        header = result.get('header_info', {})
        print("文件头信息:")
        for key, val in header.items():
            print(f"  {key}: {val}")
        print()
        
        sections = result.get('sections', [])
        if sections:
            print(f"发现的Section ({len(sections)}个):")
            for s in sections:
                print(f"  - {s['name']}: offset=0x{s['seeker']:X}, size={s['size']}")
            print()
        
        layers = result.get('layer_references', [])
        if layers:
            print(f"图层引用 ({len(layers)}个):")
            for layer in sorted(layers)[:30]:
                print(f"  - {layer}")
            print()
        
        objects = result.get('potential_objects', [])
        if objects:
            print(f"对象类型统计:")
            for obj in objects[:15]:
                print(f"  - {obj['type']}: {obj['count']} 个引用")
            print()
        
        texts = result.get('text_strings', [])
        if texts:
            print(f"文本字符串 ({len(texts)}个唯一):")
            for text in sorted(texts, key=len, reverse=True)[:30]:
                print(f"  - {text}")
            print()
        
        errors = result.get('errors', [])
        if errors:
            print("错误:")
            for err in errors:
                print(f"  ! {err}")
            print()
        
        print("=" * 60)
        print("注意: DWG 2018+ 对象数据是加密的，上述数据来自文件扫描")
        print("      完整解析需要 ezdxf + ODAFileConverter 进行格式转换")
        print("=" * 60)


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 dwg2018_deep.py <dwg_file>")
        sys.exit(1)
    
    parser = DWG2018DeepParser(sys.argv[1])
    result = parser.parse()
    parser.print_report(result)
    return result


if __name__ == "__main__":
    main()
