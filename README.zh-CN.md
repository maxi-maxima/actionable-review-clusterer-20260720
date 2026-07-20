# actionable-review-clusterer

## 痛点
代码评审常常一次涌来很多评论，团队需要先判断哪些是 bug、测试、安全、文档还是纯样式问题，否则很容易在噪音里迷路。

## 为什么现在值得做
AI 代码审查和更快的评审流正在升温；真正缺的是把评论变成可执行计划，而不是只生成更多评论。

## 安装
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -e .
```

## 运行
```bash
python -m reviewcluster examples/comments.json
cat examples/comments.json | python -m reviewcluster --json
```

## 示例
输入:
```json
[{"file":"app.py","line":12,"body":"Add a test for the retry path"}]
```
输出:
```text
# Actionable review map
Total comments: 1
...
```

## 路线图
- 加入更强的关键词和语义聚类。
- 输出 GitHub review thread ID 与负责人。
- 支持生成可直接贴回 PR 的 markdown。

## License
MIT
