"""
DWG 2018 (AC1032) Section Map 解析器

尝试读取DWG文件的内部Section结构，
进而提取图层名和基本对象信息。
"""

import struct
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass


@dataclass
class DWGSection:
    """DWG Section定义"""
    name: str
    seeker: int      # 在文件中的偏移
    size: int        # 大小
    page_count: int
    max_decomp_size: int
    unknown2: int
    compressed: int
    page_size: int
    # 页面映射
    pages: List[Tuple[int, int]]  # (page_offset, page_size)


class DWG2018Parser:
    """DWG 2018格式解析器"""
    
    def __init__(self, filepath: str):
        self.filepath = filepath
        self.version = None
        self.header_data = None
        self.sections: List[DWGSection] = []
    
    def parse(self) -> Dict:
        """解析DWG文件"""
        result = {
            'version': None,
            'sections': [],
            'layer_names': [],
            'objects_count': 0,
            'errors': []
        }
        
        try:
            with open(self.filepath, 'rb') as f:
                data = f.read()
            
            # 1. 验证版本
            version_bytes = data[0:6]
            self.version = version_bytes.decode('ascii')
            result['version'] = self.version
            
            if not self.version.startswith('AC10'):
                result['errors'].append(f"未知版本: {self.version}")
                return result
            
            # 2. 读取文件头
            # DWG 2018 文件头结构（0x00-0x100）:
            # 0x00-0x05: 版本字符串 "AC1032"
            # 0x06-0x0B: 维护版本号 + 图片搜索偏移
            # 0x0D: 0x00 (未知)
            # 0x0E-0x0F: 代码页
            # 0x10-0x17: 安全标志 + 未知
            # 0x18-0x1F: 摘要信息地址 (0)
            # 0x20-0x23: VBA项目地址
            # 0x24-0x27: 0x80 (段页大小?)
            # 0x28-0x2F: Section Map 的 Seeker (2C-2F)
            
            # 读取Section Map位置
            # 实际上，DWG 2018的section map位置在文件头结束后的加密数据中
            
            # 3. 尝试读取Section Map
            self._parse_section_map(data)
            
            result['sections'] = [
                {'name': s.name, 'offset': s.seeker, 'size': s.size, 'pages': len(s.pages)}
                for s in self.sections
            ]
            
            # 4. 尝试从Object段提取图层名
            layer_names = self._extract_layer_names(data)
            result['layer_names'] = layer_names
            
            # 5. 估算对象数量
            result['objects_count'] = self._estimate_objects(data)
            
        except Exception as e:
            result['errors'].append(str(e))
        
        return result
    
    def _parse_section_map(self, data: bytes):
        """解析Section Map"""
        # DWG 2018的文件头在0x80之后是加密的Section Locator Records
        # 我们需要解密这部分才能读取section map
        
        # 简化方法：尝试在文件末尾查找已知的section名称
        # Section Map 通常出现在文件末尾附近
        
        # 已知的DWG section名称
        known_sections = [
            b'AcDb:FileDepList', b'AcDb:Preview', b'AcDb:SummaryInfo',
            b'AcDb:RevHistory', b'AcDb:AcDsPrototype_1b', b'AcDb:FILL',
            b'AcDb:AcDbObjects', b'AcDb:Classes', b'AcDb:Handles',
            b'AcDb:AuxHeader'
        ]
        
        # 在文件中搜索这些section名称
        for section_name in known_sections:
            offset = 0
            while True:
                idx = data.find(section_name, offset)
                if idx == -1:
                    break
                
                # 找到一个section
                self.sections.append(DWGSection(
                    name=section_name.decode('ascii', errors='replace'),
                    seeker=idx,
                    size=0,
                    page_count=0,
                    max_decomp_size=0,
                    unknown2=0,
                    compressed=0,
                    page_size=0,
                    pages=[]
                ))
                offset = idx + 1
    
    def _extract_layer_names(self, data: bytes) -> List[str]:
        """尝试提取图层名"""
        layers = []
        
        # DWG 2018中图层名的特征：
        # 图层对象类型 = 0x02 (LAYER)
        # 图层名通常以 "0" (默认图层) 开始
        
        # 方法1: 搜索 "0" 图层（默认图层总是在）
        # 方法2: 搜索常见的图层名模式
        common_layer_patterns = [
            b'0\x00', b'DEFPOINTS\x00',
            '绿化\x00'.encode('utf-8'), '绿地\x00'.encode('utf-8'),
            '草坪\x00'.encode('utf-8'), '建筑\x00'.encode('utf-8'),
            '道路\x00'.encode('utf-8'), '围墙\x00'.encode('utf-8'),
            '水管\x00'.encode('utf-8'), '阀门\x00'.encode('utf-8'),
            '喷头\x00'.encode('utf-8'),
            b'GREEN\x00', b'LAWN\x00', b'BUILDING\x00',
        ]
        
        for pattern in common_layer_patterns:
            offset = 0
            while True:
                idx = data.find(pattern, offset)
                if idx == -1:
                    break
                
                # 尝试读取图层名（到下一个null字节）
                name_bytes = bytearray()
                i = idx
                while i < len(data) and data[i] != 0 and len(name_bytes) < 50:
                    name_bytes.append(data[i])
                    i += 1
                
                try:
                    name = name_bytes.decode('utf-8', errors='replace').strip()
                    if len(name) >= 1 and len(name) <= 50:
                        layers.append(name)
                except:
                    pass
                
                offset = idx + 1
        
        # 去重
        return list(set(layers))
    
    def _estimate_objects(self, data: bytes) -> int:
        """估算对象数量"""
        # DWG 2018对象数量的一个近似值可以通过文件大小估算
        # 通常一个对象占用50-500字节
        avg_obj_size = 200
        return len(data) // avg_obj_size
    
    def print_report(self, result: Dict):
        """打印解析报告"""
        print("=" * 60)
        print(f"DWG {result.get('version', 'Unknown')} 解析报告")
        print("=" * 60)
        print()
        
        sections = result.get('sections', [])
        print(f"发现的Section数量: {len(sections)}")
        for s in sections[:10]:
            print(f"  - {s['name']} (offset: 0x{s['offset']:X}, size: {s['size']})")
        
        print()
        layers = result.get('layer_names', [])
        if layers:
            print(f"提取到的图层名({len(layers)}个):")
            for layer in sorted(layers)[:20]:
                print(f"  - {layer}")
        else:
            print("未能提取到图层名（DWG 2018格式加密了对象数据）")
        
        print()
        print(f"估算对象数量: ~{result.get('objects_count', 0)}")
        
        errors = result.get('errors', [])
        if errors:
            print()
            print("错误:")
            for err in errors:
                print(f"  ! {err}")
        
        print()
        print("=" * 60)
        print("说明: DWG 2018+ 对象数据是加密的，需要转换为DXF才能完整解析")
        print("=" * 60)


def main():
    import sys
    if len(sys.argv) < 2:
        print("用法: python3 dwg2018_parser.py <dwg_file>")
        sys.exit(1)
    
    parser = DWG2018Parser(sys.argv[1])
    result = parser.parse()
    parser.print_report(result)


if __name__ == "__main__":
    main()
