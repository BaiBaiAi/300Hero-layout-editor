# 贡献指南

1. 使用 Python 3.10 或更高版本。
2. 运行 `python -m pip install -e .` 安装依赖。
3. 修改后运行 `python -m compileall -q .` 检查 Python 文件，并运行 `node --check web/app.js` 检查前端脚本。
4. JMP 写入代码必须保留边界、条目路径、MD5 和写后回读校验。
5. 不要提交游戏资源、个人游戏路径、备份、导出文件或用户布局。
6. 提交应说明触发条件、修改后的行为和验证方式。
