"""
布尔表达式搜索 —— 词法分析 + 递归下降解析 + 求值

语法（操作符必须全大写，否则按普通搜索词处理）：
  unit kill        词项之间的空格视为隐式 AND，等价于 unit AND kill
  unit AND kill    同时包含 unit 与 kill
  unit OR kill     包含 unit 或 kill 其一
  unit NOT kill    包含 unit 但不包含 kill（NOT 为一元前缀操作符）
  "unit kill"      双引号包裹的短语做整体匹配
  unit AND (kill OR combat)  圆括号指定分组优先级

宽松策略（便于边输入边搜索的中间态）：
  - 末尾悬空的 AND / OR / NOT 忽略（如 "unit AND"）
  - 未闭合的左括号在表达式末尾自动闭合（如 "unit AND (kill"）
  - 引号未闭合时短语取行尾剩余内容（如 "unit doc）
  - 表达式后多出的孤立右括号忽略（如 "unit)"）
  - 空括号分组忽略（如按调用形式搜索 "GetDamage()"）
其余结构错误（如 "unit AND OR kill"）抛出 BoolSyntaxError，
由调用方（搜索面板）向用户显示提示。

求值规则（保持与旧版纯 AND 搜索相同的排序兼容性）：
  词项/短语按字段优先级取首个命中字段的得分；
  AND 取各分支得分之和；OR 取命中分支的最高分；NOT 命中不计分。
"""
import re


class BoolSyntaxError(Exception):
    """布尔表达式语法错误。"""


# 词法类型
_LPAREN = "("
_RPAREN = ")"
_AND = "AND"
_OR = "OR"
_NOT = "NOT"
_ATOM = "ATOM"

# 单词内不能出现的字符：空白、引号（开始短语）、括号（独立符号）
_WORD_BREAK = re.compile(r'[\s"()]')


def _tokenize(query: str) -> list:
    """词法分析。

    返回 [(类型, 文本), ...]；ATOM 文本已小写化，空短语被丢弃。
    仅全大写的 AND / OR / NOT 视作操作符，其余一律转为搜索词。
    """
    tokens = []
    i, n = 0, len(query)
    while i < n:
        ch = query[i]
        if ch.isspace():
            i += 1
        elif ch == _LPAREN:
            tokens.append((_LPAREN, ch))
            i += 1
        elif ch == _RPAREN:
            tokens.append((_RPAREN, ch))
            i += 1
        elif ch == '"':
            end = query.find('"', i + 1)
            if end == -1:  # 引号未闭合：短语取行尾剩余内容（宽松处理）
                text, i = query[i + 1:], n
            else:
                text, i = query[i + 1:end], end + 1
            text = text.strip().lower()
            if text:
                tokens.append((_ATOM, text))
        else:
            match = _WORD_BREAK.search(query, i)
            j = match.start() if match else n
            word = query[i:j]
            i = j
            if word in (_AND, _OR, _NOT):
                tokens.append((word, word))
            else:
                tokens.append((_ATOM, word.lower()))
    return tokens


class _Parser:
    """递归下降解析器。

    文法（优先级从低到高）：
      or_expr  := and_expr (OR and_expr)*
      and_expr := unary ((AND)? unary)*        # 词项间空格为隐式 AND
      unary    := NOT unary | primary
      primary  := '(' or_expr ')' | 词项 | 短语
    """

    # 能够开启一个 primary 的词法类型（用于隐式 AND 循环）
    _PRIMARY_HEADS = (_ATOM, _LPAREN, _NOT)

    def __init__(self, tokens: list):
        self._tokens = tokens
        self._pos = 0

    def _peek(self):
        """查看当前词法类型，输入耗尽返回 None。"""
        return self._tokens[self._pos][0] if self._pos < len(self._tokens) else None

    def _next(self):
        """消耗并返回当前词法单元。"""
        token = self._tokens[self._pos]
        self._pos += 1
        return token

    def parse(self):
        """解析整个表达式，返回 AST 根节点。

        无任何有效词项时返回 None；表达式后多出的孤立右括号被容忍，
        其余无法消耗的残留内容抛出 BoolSyntaxError。
        """
        node = self._parse_or()
        rest = [kind for kind, _ in self._tokens[self._pos:]]
        if any(kind != _RPAREN for kind in rest):
            raise BoolSyntaxError("表达式末尾存在无法解析的内容")
        return node

    def _parse_or(self):
        children = []
        node = self._parse_and()
        if node is not None:
            children.append(node)
        while self._peek() == _OR:
            self._next()
            node = self._parse_and()
            if node is None:
                break  # 末尾悬空 OR：忽略
            children.append(node)
        if not children:
            return None
        return children[0] if len(children) == 1 else (_OR, children)

    def _parse_and(self):
        children = []
        node = self._parse_unary()
        if node is not None:
            children.append(node)
        while True:
            kind = self._peek()
            if kind == _AND:
                self._next()
                node = self._parse_unary()
                if node is None:
                    break  # 末尾悬空 AND：忽略
            elif kind in self._PRIMARY_HEADS:
                node = self._parse_unary()  # 词项间空格 → 隐式 AND
                if node is None:
                    break
            else:
                break
            children.append(node)
        if not children:
            return None
        return children[0] if len(children) == 1 else (_AND, children)

    def _parse_unary(self):
        if self._peek() == _NOT:
            self._next()
            child = self._parse_unary()
            if child is None:
                return None  # 末尾悬空 NOT：忽略
            return (_NOT, child)
        return self._parse_primary()

    def _parse_primary(self):
        kind = self._peek()
        if kind == _ATOM:
            _, text = self._next()
            return (_ATOM, text)
        if kind == _LPAREN:
            self._next()
            node = self._parse_or()
            if self._peek() == _RPAREN:
                self._next()
            # peek 为 None → 未闭合括号自动闭合（宽松处理）；
            # peek 为其它 → 括号已被内层空括号逻辑闭合，剩余内容交外层继续解析
            return node
        if kind == _RPAREN:
            # 空括号分组（如按调用形式搜索 "GetDamage()"）：宽松忽略
            if self._pos > 0 and self._tokens[self._pos - 1][0] == _LPAREN:
                self._next()
                return None
            raise BoolSyntaxError(self._missing_term_error())
        if kind in (_AND, _OR, _NOT):
            if self._pos + 1 >= len(self._tokens):
                return None  # 末尾悬空操作符：忽略
            raise BoolSyntaxError(self._missing_term_error())
        return None  # 输入耗尽

    def _missing_term_error(self) -> str:
        """构造“缺少搜索词”类错误的提示文本。

        按出错位置的前一个记号点名两侧的操作符，例如
        "unit AND OR kill" → “AND”与“OR”之间缺少搜索词，
        "(kill OR)" → “OR”后缺少搜索词。
        """
        kind, text = self._tokens[self._pos]
        prev_kind, prev_text = (
            self._tokens[self._pos - 1] if self._pos > 0 else (None, None)
        )
        if kind == _RPAREN:
            # 期望搜索词的位置出现了右括号
            if prev_kind in (_AND, _OR, _NOT):
                return f"“{prev_text}”后缺少搜索词"
            if prev_kind is None:
                return "多余的右括号"  # 如以 ")" 开头
            return "括号内缺少搜索词"  # 如 "()"（prev 为左括号）
        # 期望搜索词的位置出现了操作符
        if self._pos == 0:
            return f"表达式不能以“{text}”开头"
        if prev_kind in (_AND, _OR, _NOT):
            return f"“{prev_text}”与“{text}”之间缺少搜索词"
        if prev_kind == _LPAREN:
            return f"括号内“{text}”前缺少搜索词"
        return f"“{text}”处缺少搜索词"


def parse(query: str):
    """解析布尔表达式。

    返回 AST 根节点；输入为空或不含任何有效词项时返回 None；
    结构无法理解时抛出 BoolSyntaxError（含括号/NOT 嵌套过深的情况，
    避免递归下降解析器触发 Python 递归上限崩溃）。
    """
    tokens = _tokenize(query)
    if not tokens:
        return None
    try:
        return _Parser(tokens).parse()
    except RecursionError:
        raise BoolSyntaxError("表达式嵌套过深") from None


def _match_atom(needle: str, fields: list):
    """按字段优先级匹配单个词项/短语，返回 (是否命中, 得分)。"""
    for text, score in fields:
        if needle in text:
            return True, score
    return False, 0


def evaluate(node, fields: list):
    """对 AST 求值。

    fields: [(小写文本, 命中得分), ...] —— 同一条目内的各可搜索字段，
    按优先级排列。返回 (是否命中, 总得分)。
    """
    kind = node[0]
    if kind == _ATOM:
        return _match_atom(node[1], fields)
    if kind == _NOT:
        matched, _ = evaluate(node[1], fields)
        return (not matched), 0
    children = node[1]
    if kind == _AND:
        total = 0
        for child in children:
            matched, score = evaluate(child, fields)
            if not matched:
                return False, 0
            total += score
        return True, total
    # OR：取命中分支的最高分
    best = 0
    any_matched = False
    for child in children:
        matched, score = evaluate(child, fields)
        if matched:
            any_matched = True
            best = max(best, score)
    return any_matched, best


def search_entries(entries: list, query: str, fields_of):
    """对 entries 执行布尔搜索的通用入口。

    fields_of(entry) 返回该条目的 [(小写文本, 得分), ...] 字段列表。
    返回 (results, error)：
      - 解析成功（含无有效词项，此时 results 为全量条目）→ error 为 None
      - 语法错误 → results 为空列表，error 为提示文本
    """
    try:
        node = parse(query)
        if node is None:
            return list(entries), None

        scored = []
        for entry in entries:
            matched, score = evaluate(node, fields_of(entry))
            if matched:
                scored.append((score, entry))

        scored.sort(key=lambda x: -x[0])  # 稳定排序：同分保持数据原序
        return [entry for _, entry in scored], None
    except BoolSyntaxError as exc:
        return [], str(exc)
    except RecursionError:
        # 极深嵌套在求值阶段的兜底（解析阶段通常已拦截）
        return [], "表达式嵌套过深"
