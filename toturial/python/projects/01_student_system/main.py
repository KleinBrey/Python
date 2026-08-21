"""
==================================================
综合实战 1：学生成绩管理（class + list + JSON + pathlib）
==================================================

默认使用临时文件，因此运行不会污染项目目录。
"""

import json
from dataclasses import asdict, dataclass
from pathlib import Path
from tempfile import TemporaryDirectory

@dataclass
class Student:
    name: str
    scores: list[float]

    @property
    def average(self) -> float:
        return sum(self.scores) / len(self.scores) if self.scores else 0.0


class StudentSystem:
    def __init__(self) -> None:
        self.students: list[Student] = []

    def add(self, student: Student) -> None:
        self.students.append(student)

    def ranking(self) -> list[Student]:
        return sorted(self.students, key=lambda item: item.average, reverse=True)

    def save(self, path: Path) -> None:
        data = [asdict(student) for student in self.students]
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")


def main() -> None:
    system = StudentSystem()
    system.add(Student("小林", [88, 92, 85]))
    system.add(Student("小王", [95, 90, 93]))
    for rank, student in enumerate(system.ranking(), start=1):
        print(f"{rank}. {student.name} 平均分 {student.average:.1f}")
    with TemporaryDirectory() as directory:
        path = Path(directory) / "students.json"
        system.save(path)
        print("JSON：", path.read_text(encoding="utf-8"))


if __name__ == "__main__":
    main()

"""
练习：增加按姓名查找和删除学生；保存时记录 average。
"""
