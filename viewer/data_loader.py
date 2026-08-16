"""
数据加载与搜索模块

职责：
  - 从 api_enhanced.json 加载增强后的 API 数据
  - 构建层级索引（根对象 → 函数A → 函数B）
  - 提供模糊搜索功能（匹配最终函数名、displayName 与备注）
"""
import json
import os


_DEFAULT_DATA_PATH = os.path.join(
    os.path.dirname(os.path.abspath(__file__)), "..", "data", "api_enhanced.json"
)


class ApiDataLoader:
    """
    API 数据加载器。

    属性：
      metadata: 元数据字典
      entries: 所有函数条目的扁平列表
      root_index: 层级索引 {table: {funcA: {funcB: [entries]}}}
    """

    def __init__(self, data_path=None):
        if data_path is None:
            data_path = _DEFAULT_DATA_PATH
        self.metadata = {}
        self.entries = []
        self.root_index = {}  # {table: {"_all": [...], funcA: {"_all": [...], funcB: [...]}}}
        self._load(data_path)

    def _load(self, data_path: str):
        """加载数据并构建层级索引。"""
        with open(data_path, "r", encoding="utf-8") as f:
            data = json.load(f)

        self.metadata = data.get("metadata", {})

        for category, entries in data.get("objects", {}).items():
            for key, entry in entries.items():
                entry["_category"] = category
                entry["_key"] = key
                self.entries.append(entry)

                # 构建层级索引
                table = entry.get("table", "")
                func_a = entry.get("functionA", "")
                func_b = entry.get("functionB", "")

                if not table:
                    continue

                # 根对象层
                if table not in self.root_index:
                    self.root_index[table] = {"_all": []}
                self.root_index[table]["_all"].append(entry)

                # 函数A层
                if func_a:
                    if func_a not in self.root_index[table]:
                        self.root_index[table][func_a] = {"_all": []}
                    self.root_index[table][func_a]["_all"].append(entry)

                    # 函数B层
                    if func_b:
                        if func_b not in self.root_index[table][func_a]:
                            self.root_index[table][func_a][func_b] = []
                        self.root_index[table][func_a][func_b].append(entry)

    def get_root_objects(self) -> list:
        """获取所有根对象名的排序列表。"""
        return sorted(self.root_index.keys())

    def get_functions_a(self, root: str) -> list:
        """获取指定根对象下所有唯一的 function 值。"""
        if root not in self.root_index:
            return []
        return sorted(k for k in self.root_index[root] if k != "_all")

    def get_functions_b(self, root: str, func_a: str) -> list:
        """获取指定根对象+函数A下所有唯一的 functionB 值。"""
        if root not in self.root_index:
            return []
        if func_a not in self.root_index[root]:
            return []
        return sorted(k for k in self.root_index[root][func_a] if k != "_all")

    def get_entries(self, root: str = "", func_a: str = "", func_b: str = "") -> list:
        """根据层级筛选获取条目。"""
        if not root:
            return self.entries
        if root not in self.root_index:
            return []
        if not func_a:
            return self.root_index[root]["_all"]
        if func_a not in self.root_index[root]:
            return []
        if not func_b:
            return self.root_index[root][func_a]["_all"]
        if func_b not in self.root_index[root][func_a]:
            return []
        return self.root_index[root][func_a][func_b]

    def search(self, query: str) -> list:
        """
        模糊搜索函数。

        搜索范围：最终函数名、displayName、notes
        搜索逻辑：空格分隔多个关键词，所有关键词都必须匹配
        排序：函数名匹配 > 显示名 > 备注
        """
        if not query:
            return self.entries

        terms = query.lower().strip().split()
        results = []

        for entry in self.entries:
            display_name = entry.get("displayName", "").lower()
            notes = " ".join(entry.get("notes", [])).lower()

            # 确定最终函数名（链式取最后一个）
            final_func = entry.get("functionA", "").lower()
            for suffix in ("B", "C", "D"):
                fb = entry.get(f"function{suffix}", "")
                if fb:
                    final_func = fb.lower()
                else:
                    break

            score = 0
            all_match = True
            for term in terms:
                if term in final_func:
                    score += 100
                elif term in display_name:
                    score += 60
                elif term in notes:
                    score += 20
                else:
                    all_match = False
                    break

            if all_match:
                results.append((score, entry))

        results.sort(key=lambda x: -x[0])
        return [r[1] for r in results]
