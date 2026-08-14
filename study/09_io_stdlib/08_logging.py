"""
==================================================
知识点：logging 日志
==================================================
"""

import logging

# basicConfig 适合小脚本；大型项目通常在程序入口集中配置一次。
logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s | %(levelname)s | %(name)s | %(message)s",
)
logger = logging.getLogger(__name__)

logger.debug("DEBUG：开发调试细节")
logger.info("INFO：正常业务过程")
logger.warning("WARNING：可继续但值得关注")
logger.error("ERROR：某项操作失败")
logger.critical("CRITICAL：系统可能无法继续")

symbol = "600519"
price = 1688.0
# 使用占位符让日志库在需要输出该级别时再格式化，优于提前构造 f-string。
logger.info("获取行情成功 symbol=%s price=%.2f", symbol, price)

try:
    int("错误数字")
except ValueError:
    logger.exception("解析失败")  # 在 except 中记录堆栈，便于排查

# print 适合学习和用户直接输出；logging 有级别、时间、来源、文件轮转等能力。

"""
本节总结：按严重程度选择级别；模块 logger 使用 __name__；异常用 logger.exception。
"""
