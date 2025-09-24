**搭建项目骨架，并完整实现 `ap e <concept>` 命令的功能。**

具体步骤包括：

1. 创建上述文件结构（`main.py`, `requirements.txt`, `.env.example`）。
2. 在 `main.py` 中，使用 Typer 设置好 CLI 应用的基本框架。
3. 实现 `e` 命令函数，它接受一个 `concept` 字符串作为参数。
4. 在该函数内，实现：
    * 加载 `.env` 文件中的 DEEPSEEK_API_KEY。
    * 创建 `workspace/explanation` 目录（如果不存在）。
    * 构建精良的 Prompt（参考 `全局文档.md`）。
    * 调用 DeepSeek API 获取 Markdown 文本。
    * 将返回的文本保存到 `workspace/explanation` 目录下的 `<concept>.md` 文件中。
    * 向用户打印一条成功的消息，例如：`✅ 解释已生成并保存到: workspace/explanation/函数式编程.md`。

## 完成的标准

1. 运行 `pip install -e .` 后，`ap` 命令可用。
2. 运行 `ap e "some concept"` 能够成功调用 DeepSeek API 并生成解释文档。
3. 生成的 Markdown 文档内容质量高，结构清晰，符合 `全局文档.md` 中定义的标准。
4. 文档被正确保存到 `workspace/explanation/<concept>.md`。
