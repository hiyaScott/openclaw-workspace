#!/usr/bin/env python3
"""
奥数学习助手 - 小学奥数精讲与测试（第三版）
支持分年级学习、知识点查询、例题练习
"""

import json
import os
import random

# 知识库数据
MATH_KNOWLEDGE = {
    "grade_1": {
        "name": "一年级",
        "topics": [
            {"id": 1, "name": "速算与巧算(一)", "key_points": ["凑十法", "凑整法", "带符号搬家"], "methods": ["看个位凑十", "找好朋友数"]},
            {"id": 2, "name": "速算与巧算(二)", "key_points": ["加法补数", "减法凑整", "基准数法"], "methods": ["凑百凑千", "找基准数计算"]},
            {"id": 3, "name": "数一数(一)", "key_points": ["点线角计数"], "methods": ["分类计数", "标记法"]},
            {"id": 4, "name": "数一数(二)", "key_points": ["图形计数"], "methods": ["按大小分类", "按位置分类"]},
            {"id": 5, "name": "比一比", "key_points": ["长短比较", "高矮比较", "轻重比较"], "methods": ["直接观察", "工具测量", "间接比较"]},
            {"id": 6, "name": "数图形", "key_points": ["平面图形识别"], "methods": ["边数特征", "角数特征"]},
            {"id": 7, "name": "摆一摆", "key_points": ["火柴棒游戏"], "methods": ["移动火柴", "添加火柴", "去掉火柴"]},
            {"id": 8, "name": "智趣问题", "key_points": ["趣味数学"], "methods": ["脑筋急转弯", "逆向思维"]},
            {"id": 9, "name": "数阵图(一)", "key_points": ["简单数阵"], "methods": ["找公共位置", "计算线和"]},
            {"id": 10, "name": "数阵图(二)", "key_points": ["辐射型数阵", "封闭型数阵"], "methods": ["中心数确定", "边和计算"]},
            {"id": 11, "name": "认识时钟", "key_points": ["整点半点", "时间计算"], "methods": ["时针分针关系", "加减时间"]},
            {"id": 12, "name": "植树问题", "key_points": ["间隔问题"], "methods": ["两端都种:棵数=段数+1", "一端种:棵数=段数", "两端不种:棵数=段数-1"]},
            {"id": 13, "name": "图形中的计数", "key_points": ["复杂图形计数"], "methods": ["分层计数", "分区域计数"]},
            {"id": 14, "name": "智力趣题", "key_points": ["逻辑推理"], "methods": ["排除法", "假设法"]},
            {"id": 15, "name": "有趣的一笔画", "key_points": ["一笔画判断"], "methods": ["数奇点", "0或2个奇点可一笔画"]},
            {"id": 16, "name": "简单的年龄问题", "key_points": ["年龄差不变"], "methods": ["年龄差永远相等", "画线段图"]},
            {"id": 17, "name": "巧解应用题", "key_points": ["图解法", "假设法"], "methods": ["画示意图", "假设调整"]},
            {"id": 18, "name": "智巧问题", "key_points": ["数学游戏"], "methods": ["必胜策略", "对称思想"]},
            {"id": 19, "name": "火柴棒游戏", "key_points": ["图形变换"], "methods": ["改变数字", "改变运算符", "改变图形"]},
            {"id": 20, "name": "趣味问题", "key_points": ["综合应用"], "methods": ["灵活运用所学知识"]},
        ]
    },
    "grade_2": {
        "name": "二年级",
        "topics": [
            {"id": 1, "name": "速算与巧算", "key_points": ["乘法凑整", "除法性质", "运算律"], "methods": ["乘法交换律", "乘法结合律", "乘法分配律"]},
            {"id": 2, "name": "数数与计数", "key_points": ["分类计数", "枚举法"], "methods": ["不重不漏", "有序枚举"]},
            {"id": 3, "name": "找规律填数", "key_points": ["等差数列", "等比数列", "周期数列"], "methods": ["看相邻差", "看相邻倍", "找周期"]},
            {"id": 4, "name": "找规律填图", "key_points": ["图形旋转", "平移", "对称"], "methods": ["观察位置变化", "观察方向变化"]},
            {"id": 5, "name": "巧填算符", "key_points": ["添加运算符号"], "methods": ["倒推法", "凑数法", "尝试法"]},
            {"id": 6, "name": "算式谜", "key_points": ["横式谜", "竖式谜"], "methods": ["个位分析", "进位分析", "范围估计"]},
            {"id": 7, "name": "数图形(一)", "key_points": ["线段计数", "角计数"], "methods": ["基本线段法", "公式法:n(n-1)/2"]},
            {"id": 8, "name": "数图形(二)", "key_points": ["三角形计数", "长方形计数"], "methods": ["分类数", "长边线段数×宽边线段数"]},
            {"id": 9, "name": "一笔画问题", "key_points": ["奇点偶点", "欧拉路径"], "methods": ["数奇点数", "0奇点:起点终点同", "2奇点:起终点在奇点"]},
            {"id": 10, "name": "简单的周期问题", "key_points": ["周期现象", "余数应用"], "methods": ["找周期长度", "用总数÷周期", "看余数定答案"]},
            {"id": 11, "name": "移多补少", "key_points": ["平均数思想"], "methods": ["差额平分", "先求差再÷2"]},
            {"id": 12, "name": "还原问题", "key_points": ["逆推法"], "methods": ["从结果倒推", "操作逆序", "画流程图"]},
            {"id": 13, "name": "植树问题", "key_points": ["封闭图形", "双边植树"], "methods": ["封闭:棵数=段数", "双边:单边×2"]},
            {"id": 14, "name": "简单推理", "key_points": ["列表法", "假设法", "排除法"], "methods": ["画表格整理信息", "假设验证", "排除不可能"]},
            {"id": 15, "name": "巧解应用题", "key_points": ["和差问题初步", "和倍问题初步"], "methods": ["和差公式", "画线段图"]},
            {"id": 16, "name": "智巧问题", "key_points": ["数学趣题"], "methods": ["分析题意", "找关键点"]},
            {"id": 17, "name": "画图法解应用题", "key_points": ["线段图", "示意图"], "methods": ["画线段表示数量", "标出已知条件"]},
            {"id": 18, "name": "简单枚举", "key_points": ["有序枚举", "分类枚举"], "methods": ["按顺序列举", "先分类再枚举"]},
            {"id": 19, "name": "趣味问题", "key_points": ["数学游戏"], "methods": ["逻辑分析", "策略思考"]},
            {"id": 20, "name": "综合练习", "key_points": ["知识综合"], "methods": ["灵活运用"]},
        ]
    },
    "grade_3": {
        "name": "三年级",
        "topics": [
            {"id": 1, "name": "速算与巧算", "key_points": ["乘法分配律", "提取公因数"], "methods": ["凑整提取公因数", "变形提取公因数"]},
            {"id": 2, "name": "平均数", "key_points": ["平均数概念", "移多补少"], "methods": ["总和÷个数", "基准数法"]},
            {"id": 3, "name": "简单数列求和", "key_points": ["等差数列求和"], "methods": ["公式:(首项+末项)×项数÷2"]},
            {"id": 4, "name": "植树问题", "key_points": ["爬楼梯", "锯木头", "敲钟"], "methods": ["爬楼梯:楼层差=楼梯段数", "锯木头:段数=次数+1"]},
            {"id": 5, "name": "方阵问题", "key_points": ["实心方阵", "空心方阵"], "methods": ["实心:总数=边长×边长", "空心:总数=(外边长-层数)×层数×4"]},
            {"id": 6, "name": "年龄问题", "key_points": ["和差倍与年龄"], "methods": ["年龄差不变", "画年龄轴"]},
            {"id": 7, "name": "消元问题", "key_points": ["代入消元", "加减消元"], "methods": ["代入法", "加减法消去一个未知数"]},
            {"id": 8, "name": "逆推问题", "key_points": ["从结果倒推", "操作逆序"], "methods": ["画流程图", "从后往前算", "加减互逆", "乘除互逆"]},
            {"id": 9, "name": "简单的逻辑推理", "key_points": ["真假判断", "表格推理"], "methods": ["假设法", "矛盾分析法", "列表整理"]},
            {"id": 10, "name": "奇数与偶数", "key_points": ["奇偶性分析"], "methods": ["奇+奇=偶", "偶+偶=偶", "奇+偶=奇", "奇×奇=奇"]},
            {"id": 11, "name": "除法与余数", "key_points": ["带余除法", "余数性质"], "methods": ["被除数=除数×商+余数", "余数<除数"]},
            {"id": 12, "name": "数线段", "key_points": ["公式法"], "methods": ["n个点有n(n-1)/2条线段"]},
            {"id": 13, "name": "数图形", "key_points": ["复杂图形计数"], "methods": ["分类计数", "公式法"]},
            {"id": 14, "name": "巧求周长", "key_points": ["平移法", "标向法"], "methods": ["平移成规则图形", "左右和=上下和"]},
            {"id": 15, "name": "定义新运算", "key_points": ["自定义运算"], "methods": ["理解新规则", "按规则计算", "找规律"]},
            {"id": 16, "name": "混合运算与应用题", "key_points": ["四则混合"], "methods": ["先乘除后加减", "有括号先算括号"]},
            {"id": 17, "name": "归一问题", "key_points": ["正归一", "反归一"], "methods": ["先求单一量", "倍比法"]},
            {"id": 18, "name": "盈亏问题", "key_points": ["一盈一亏", "两盈两亏"], "methods": ["公式:(盈+亏)÷两次差=份数", "画线段图"]},
            {"id": 19, "name": "最大与最小", "key_points": ["极值问题"], "methods": ["极端思想", "枚举比较"]},
            {"id": 20, "name": "幻方", "key_points": ["三阶幻方"], "methods": ["中心数=总和÷3", "对角线和=边线和"]},
        ]
    },
    "grade_4": {
        "name": "四年级",
        "topics": [
            {"id": 1, "name": "速算与巧算", "key_points": ["多位数巧算"], "methods": ["凑整", "提取公因数", "等差数列技巧"]},
            {"id": 2, "name": "和倍问题", "key_points": ["画线段图"], "methods": ["找1倍数", "画图表示倍数关系", "和÷(倍数+1)=1倍数"]},
            {"id": 3, "name": "差倍问题", "key_points": ["差倍公式"], "methods": ["差÷(倍数-1)=1倍数", "暗差问题找差"]},
            {"id": 4, "name": "和差问题", "key_points": ["和差公式"], "methods": ["大数=(和+差)÷2", "小数=(和-差)÷2"]},
            {"id": 5, "name": "年龄问题", "key_points": ["变倍问题"], "methods": ["画年龄轴", "找不变量"]},
            {"id": 6, "name": "相遇问题", "key_points": ["相遇时间"], "methods": ["路程和=速度和×时间"]},
            {"id": 7, "name": "追及问题", "key_points": ["追及时间"], "methods": ["路程差=速度差×时间"]},
            {"id": 8, "name": "火车行程问题", "key_points": ["过桥", "错车", "超车"], "methods": ["总路程=车长+桥长", "错车:路程和=两车长"]},
            {"id": 9, "name": "流水问题", "key_points": ["顺水", "逆水"], "methods": ["顺水速=船速+水速", "逆水速=船速-水速"]},
            {"id": 10, "name": "植树问题", "key_points": ["综合应用"], "methods": ["灵活运用各种情况"]},
            {"id": 11, "name": "鸡兔同笼问题", "key_points": ["假设法", "抬腿法"], "methods": ["假设全是鸡", "假设全是兔", "方程思想"]},
            {"id": 12, "name": "数阵图", "key_points": ["辐射型", "封闭型", "复合型"], "methods": ["确定重叠数", "计算线和"]},
            {"id": 13, "name": "长方形的面积", "key_points": ["面积公式"], "methods": ["长方形面积=长×宽", "正方形面积=边长×边长"]},
            {"id": 14, "name": "数谜问题", "key_points": ["加减乘除竖式谜"], "methods": ["个位分析", "高位分析", "进位分析", "范围估计"]},
            {"id": 15, "name": "图形的拼切与面积计算", "key_points": ["割补法", "旋转法"], "methods": ["割下补到别处", "旋转后重新组合"]},
            {"id": 16, "name": "巧算24点", "key_points": ["24点游戏"], "methods": ["凑3×8", "凑4×6", "凑2×12", "加减凑24"]},
            {"id": 17, "name": "逻辑问题", "key_points": ["假设推理", "矛盾分析"], "methods": ["假设-验证-排除", "找矛盾"]},
            {"id": 18, "name": "定义新运算", "key_points": ["复杂运算定义"], "methods": ["仔细理解新规则", "按步骤计算"]},
            {"id": 19, "name": "加法原理与乘法原理", "key_points": ["计数原理"], "methods": ["分类相加", "分步相乘"]},
            {"id": 20, "name": "奇数与偶数", "key_points": ["奇偶性综合"], "methods": ["奇偶分析", "奇偶运算性质"]},
        ]
    },
    "grade_5": {
        "name": "五年级",
        "topics": [
            {"id": 1, "name": "小数的巧算与大小比较", "key_points": ["小数运算技巧"], "methods": ["凑整", "提取公因数", "通分比较"]},
            {"id": 2, "name": "等差数列", "key_points": ["通项公式", "求和公式"], "methods": ["第n项=首项+(n-1)×公差", "和=(首项+末项)×项数÷2"]},
            {"id": 3, "name": "列方程解应用题", "key_points": ["设未知数", "列方程"], "methods": ["直接设元", "间接设元", "找等量关系"]},
            {"id": 4, "name": "平均数", "key_points": ["加权平均"], "methods": ["总数量÷总份数", "基准数法"]},
            {"id": 5, "name": "鸡兔同笼问题", "key_points": ["进阶题型"], "methods": ["假设法", "方程法"]},
            {"id": 6, "name": "平面图形的周长与面积", "key_points": ["各种图形公式"], "methods": ["长方形", "正方形", "平行四边形", "三角形", "梯形"]},
            {"id": 7, "name": "等积变形", "key_points": ["等高模型", "等底模型"], "methods": ["等高:面积比=底之比", "等底:面积比=高之比"]},
            {"id": 8, "name": "图形的割补与切拼", "key_points": ["面积守恒"], "methods": ["割补法", "旋转法", "对称法"]},
            {"id": 9, "name": "数的整除特征", "key_points": ["整除规则"], "methods": ["被2/5看末位", "被4/25看后两位", "被8看末三位", "被3/9看数字和", "被11看奇偶位差"]},
            {"id": 10, "name": "质数与合数", "key_points": ["质数定义"], "methods": ["100以内质数表", "质数判断方法"]},
            {"id": 11, "name": "分解质因数", "key_points": ["短除法"], "methods": ["短除法分解", "标准分解式"]},
            {"id": 12, "name": "最大公约数与最小公倍数", "key_points": ["辗转相除", "短除法"], "methods": ["辗转相除求GCD", "公式:LCM(a,b)=a×b÷GCD(a,b)"]},
            {"id": 13, "name": "数阵问题", "key_points": ["复杂数阵"], "methods": ["确定关键位置", "最值分析"]},
            {"id": 14, "name": "周期问题", "key_points": ["综合周期"], "methods": ["找周期", "余数定答案"]},
            {"id": 15, "name": "盈亏问题", "key_points": ["进阶题型"], "methods": ["公式法", "方程法"]},
            {"id": 16, "name": "完全平方数", "key_points": ["平方数性质"], "methods": ["个位特征", "范围估计"]},
            {"id": 17, "name": "相遇和追及问题", "key_points": ["多次相遇"], "methods": ["画图分析", "比例法"]},
            {"id": 18, "name": "流水行船问题", "key_points": ["相遇追及与流水"], "methods": ["速度和与速度差不受水速影响"]},
            {"id": 19, "name": "有余数的除法", "key_points": ["余数定理"], "methods": ["余数小于除数", "被除数=除数×商+余数"]},
            {"id": 20, "name": "长方体与正方体", "key_points": ["表面积", "体积"], "methods": ["表面积公式", "体积公式", "空间想象"]},
        ]
    },
    "grade_6": {
        "name": "六年级",
        "topics": [
            {"id": 1, "name": "分数的计算", "key_points": ["分数巧算", "裂项相消"], "methods": ["裂项:1/n(n+1)=1/n-1/(n+1)", "凑整"]},
            {"id": 2, "name": "分数的大小比较", "key_points": ["通分", "交叉相乘"], "methods": ["通分母", "通分子", "交叉相乘", "倒数比较"]},
            {"id": 3, "name": "估值与取整", "key_points": ["取整函数", "放缩法"], "methods": ["[x]表示不大于x的最大整数", "{x}=x-[x]"]},
            {"id": 4, "name": "分数应用题(一)", "key_points": ["找单位1"], "methods": ["量率对应", "单位1=具体量÷对应分率"]},
            {"id": 5, "name": "分数应用题(二)", "key_points": ["转化单位1"], "methods": ["抓不变量", "统一单位1"]},
            {"id": 6, "name": "工程问题", "key_points": ["工作效率"], "methods": ["工效=工作量÷时间", "合作工效=工效和"]},
            {"id": 7, "name": "比与比例", "key_points": ["比例性质"], "methods": ["内项积=外项积", "正比例", "反比例"]},
            {"id": 8, "name": "圆与扇形", "key_points": ["周长", "面积"], "methods": ["圆周长=2πr", "圆面积=πr²", "扇形按圆心角比例"]},
            {"id": 9, "name": "圆柱与圆锥", "key_points": ["表面积", "体积"], "methods": ["圆柱表面积", "圆柱体积", "圆锥体积=1/3×底×高"]},
            {"id": 10, "name": "长方体", "key_points": ["空间切割"], "methods": ["切割表面积变化", "涂色问题"]},
            {"id": 11, "name": "行程问题", "key_points": ["复杂相遇追及"], "methods": ["画图分析", "比例行程", "多次相遇"]},
            {"id": 12, "name": "时钟问题", "key_points": ["重合", "成直线"], "methods": ["时针速度0.5°/分", "分针速度6°/分"]},
            {"id": 13, "name": "计数问题", "key_points": ["排列组合初步"], "methods": ["枚举法", "加法原理", "乘法原理", "容斥原理"]},
            {"id": 14, "name": "数论初步", "key_points": ["整除", "质数", "余数"], "methods": ["综合应用"]},
            {"id": 15, "name": "列方程解应用题", "key_points": ["复杂方程"], "methods": ["设多个未知数", "列方程组"]},
            {"id": 16, "name": "周期问题", "key_points": ["综合周期"], "methods": ["位置周期", "数值周期"]},
            {"id": 17, "name": "倒推法", "key_points": ["复杂逆推"], "methods": ["列表倒推", "分步逆推"]},
            {"id": 18, "name": "容斥原理", "key_points": ["二量重叠", "三量重叠"], "methods": ["|A∪B|=|A|+|B|-|A∩B|"]},
            {"id": 19, "name": "最大与最小", "key_points": ["极端思想"], "methods": ["最值原理", "最优方案"]},
            {"id": 20, "name": "染色问题", "key_points": ["染色论证"], "methods": ["奇偶分析", "染色法证明"]},
        ]
    }
}

# 学习进度文件
PROGRESS_FILE = os.path.expanduser("~/.openclaw/math_olympiad_progress.json")

def load_progress():
    """加载学习进度"""
    if os.path.exists(PROGRESS_FILE):
        with open(PROGRESS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_progress(progress):
    """保存学习进度"""
    os.makedirs(os.path.dirname(PROGRESS_FILE), exist_ok=True)
    with open(PROGRESS_FILE, 'w') as f:
        json.dump(progress, f, indent=2)

def list_grades():
    """列出所有年级"""
    print("\n📚 小学奥数精讲与测试（第三版）")
    print("=" * 50)
    for grade_key, grade_data in MATH_KNOWLEDGE.items():
        print(f"  {grade_data['name']} - 共{len(grade_data['topics'])}讲")
    print()

def list_topics(grade_key):
    """列出某年级的所有讲"""
    if grade_key not in MATH_KNOWLEDGE:
        print(f"❌ 无效的年级: {grade_key}")
        return
    
    grade_data = MATH_KNOWLEDGE[grade_key]
    print(f"\n📖 {grade_data['name']} 目录")
    print("=" * 50)
    
    for topic in grade_data['topics']:
        print(f"  第{topic['id']:2d}讲: {topic['name']}")
    print()

def show_topic(grade_key, topic_id):
    """显示某讲的详细内容"""
    if grade_key not in MATH_KNOWLEDGE:
        print(f"❌ 无效的年级: {grade_key}")
        return
    
    grade_data = MATH_KNOWLEDGE[grade_key]
    topic = None
    for t in grade_data['topics']:
        if t['id'] == topic_id:
            topic = t
            break
    
    if not topic:
        print(f"❌ 无效的讲次: {topic_id}")
        return
    
    print(f"\n📌 第{topic['id']}讲: {topic['name']}")
    print("=" * 50)
    print("\n🔑 核心知识点:")
    for point in topic['key_points']:
        print(f"  • {point}")
    
    print("\n🛠️ 解题方法:")
    for method in topic['methods']:
        print(f"  • {method}")
    print()

def search_topic(keyword):
    """搜索知识点"""
    print(f"\n🔍 搜索: '{keyword}'")
    print("=" * 50)
    
    found = False
    for grade_key, grade_data in MATH_KNOWLEDGE.items():
        for topic in grade_data['topics']:
            if keyword in topic['name'] or any(keyword in kp for kp in topic['key_points']):
                print(f"  {grade_data['name']} 第{topic['id']}讲: {topic['name']}")
                found = True
    
    if not found:
        print("  未找到相关知识点")
    print()

def mark_completed(grade_key, topic_id):
    """标记某讲为已完成"""
    progress = load_progress()
    
    if grade_key not in progress:
        progress[grade_key] = []
    
    if topic_id not in progress[grade_key]:
        progress[grade_key].append(topic_id)
        save_progress(progress)
        print(f"✅ 已标记完成: {grade_key} 第{topic_id}讲")
    else:
        print(f"ℹ️ 该讲已经标记为完成")

def show_progress():
    """显示学习进度"""
    progress = load_progress()
    
    print("\n📊 学习进度")
    print("=" * 50)
    
    for grade_key, grade_data in MATH_KNOWLEDGE.items():
        completed = len(progress.get(grade_key, []))
        total = len(grade_data['topics'])
        percentage = (completed / total * 100) if total > 0 else 0
        bar = "█" * int(percentage / 10) + "░" * (10 - int(percentage / 10))
        print(f"  {grade_data['name']}: {bar} {completed}/{total} ({percentage:.1f}%)")
    print()

def recommend_topic():
    """推荐学习某讲"""
    progress = load_progress()
    
    # 找第一个未完成的讲
    for grade_key, grade_data in MATH_KNOWLEDGE.items():
        completed = progress.get(grade_key, [])
        for topic in grade_data['topics']:
            if topic['id'] not in completed:
                print(f"\n💡 推荐学习")
                print("=" * 50)
                print(f"  {grade_data['name']} 第{topic['id']}讲: {topic['name']}")
                print(f"\n  使用 'math.py show {grade_key} {topic['id']}' 查看详情")
                return
    
    print("\n🎉 恭喜！你已经学完了所有内容！")

def main():
    import sys
    
    if len(sys.argv) < 2:
        print("""
奥数学习助手 - 小学奥数精讲与测试（第三版）

用法:
  math.py list                          - 列出所有年级
  math.py topics <grade>                - 列出某年级所有讲
                                           grade: grade_1 ~ grade_6
  math.py show <grade> <topic_id>       - 查看某讲详情
  math.py search <keyword>              - 搜索知识点
  math.py mark <grade> <topic_id>       - 标记某讲为已完成
  math.py progress                      - 查看学习进度
  math.py recommend                     - 推荐学习内容

示例:
  math.py list
  math.py topics grade_3
  math.py show grade_3 5
  math.py search 行程
  math.py mark grade_3 5
        """)
        return
    
    command = sys.argv[1]
    
    if command == "list":
        list_grades()
    elif command == "topics":
        if len(sys.argv) < 3:
            print("❌ 请指定年级，例如: math.py topics grade_3")
            return
        list_topics(sys.argv[2])
    elif command == "show":
        if len(sys.argv) < 4:
            print("❌ 请指定年级和讲次，例如: math.py show grade_3 5")
            return
        show_topic(sys.argv[2], int(sys.argv[3]))
    elif command == "search":
        if len(sys.argv) < 3:
            print("❌ 请指定关键词，例如: math.py search 行程")
            return
        search_topic(sys.argv[2])
    elif command == "mark":
        if len(sys.argv) < 4:
            print("❌ 请指定年级和讲次，例如: math.py mark grade_3 5")
            return
        mark_completed(sys.argv[2], int(sys.argv[3]))
    elif command == "progress":
        show_progress()
    elif command == "recommend":
        recommend_topic()
    else:
        print(f"❌ 未知命令: {command}")
        print("使用 'math.py' 查看帮助")

if __name__ == "__main__":
    main()
