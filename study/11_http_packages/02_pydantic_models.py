"""
==================================================
知识点：Pydantic BaseModel、Field、校验与序列化
==================================================

先安装：python -m pip install "pydantic>=2"
"""

try:
    from pydantic import BaseModel, Field, ValidationError, field_validator
except ImportError:
    print("缺少 pydantic，请运行：python -m pip install 'pydantic>=2'")
else:
    class Stock(BaseModel):
        symbol: str = Field(min_length=6, max_length=9, description="股票代码")
        price: float = Field(gt=0, description="价格必须大于 0")
        tags: list[str] = Field(default_factory=list)

        @field_validator("symbol", mode="before")
        @classmethod
        def normalize_symbol(cls, value: object) -> str:
            # mode="before" 让清洗先于长度约束；外部输入先统一转成字符串。
            value = str(value).strip().upper()
            if not value[:6].isdigit():
                raise ValueError("代码前 6 位必须是数字")
            return value

    # model_validate 可校验字典/兼容对象；也会按规则转换 "1688.5" 为 float。
    stock = Stock.model_validate({"symbol": " 600519.sh ", "price": "1688.5"})
    print(stock)
    print(stock.model_dump())  # 转回普通 Python dict，适合交给 JSON/数据库层

    try:
        Stock.model_validate({"symbol": "ABC", "price": -1})
    except ValidationError as error:
        print("校验错误数量：", error.error_count())

# dataclass 主要减少普通数据类样板；Pydantic 重点是外部数据解析、转换与验证。

"""
本节总结：BaseModel 声明数据模型；Field 表达约束；validator 处理自定义规则。
"""
