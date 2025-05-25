from matplotlib.font_manager import FontManager

def check_chinese_fonts():
    fm = FontManager()
    zh_fonts = [f.name for f in fm.ttflist if 'hei' in f.name.lower()]
    print("可用中文字体:", zh_fonts)

check_chinese_fonts()