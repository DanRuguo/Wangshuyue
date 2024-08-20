# 学籍照片爬取
**爬取山东科技大学2021级所有学生学籍照片**

该脚本的主要功能是从指定的URL下载包含照片的压缩文件，并解压缩到指定的文件夹中。该过程包括自动遍历学号、发送请求、下载文件和处理错误等步骤。

## 主要功能

1. **学号生成与遍历**：
   - 生成学号的格式为“2021 + 校区号 + 学院号 + 班级号 + 尾号”。
   - 脚本会从1开始遍历校区号、学院号、班级号和尾号，直至找到符合条件的学号。

2. **请求与下载**：
   - 使用 `requests` 库发送 POST 请求以验证学号的有效性。
   - 如果学号有效，脚本会构建下载链接并发送 GET 请求下载包含照片的压缩文件。

3. **文件解压缩**：
   - 下载的压缩文件会被解压到指定的文件夹中，照片文件将按学号命名保存。

4. **重试机制**：
   - 针对网络连接错误和请求错误，脚本实现了重试机制，避免因为临时网络问题导致的任务失败。

5. **状态跟踪与自动跳过**：
   - 脚本会跟踪已处理的学号，避免重复下载和处理。
   - 当某个校区或学院遍历完成时，脚本会自动跳转到下一个校区或学院，继续处理。

## 使用说明

1. **运行环境**：
   - 确保已安装 `requests`、`zipfile`、`io` 等必要的Python库。
   - 可通过命令 `pip install requests` 安装所需库。

2. **配置与执行**：
   - 直接运行脚本 `python script_name.py`（替换为实际脚本名）。
   - 脚本将自动开始从校区号01到99、学院号01到30、班级号01到99依次遍历学号并进行下载处理。

3. **获取Cookie信息**：
   - 使用学号 `202111070119` 和密码 `617424` 登录网站 [http://yktfwdt.sdust.edu.cn/](http://yktfwdt.sdust.edu.cn/)。
   - 直接访问上述网站可能进不去，手动将*https*改成*http*即可。
   - 登录后，进入浏览器开发者模式（通常按 `F12` 或 `Ctrl+Shift+I`）获取请求标头中的 `Cookie` 信息，并替换代码中的旧 `Cookie`。
   - 只有正确设置了 `Cookie` 信息后，脚本才能正常运行。

4. **输出与日志**：
   - 照片将被保存到 `photos` 文件夹中，文件名以学号命名。
   - 在控制台中显示处理进度、错误信息和成功的下载记录。

5. **错误处理**：
   - 如果网络请求失败，脚本会自动进行最多5次重试，每次重试间隔3秒。
   - 如果某个校区、学院或班级处理失败，脚本会尝试跳过到下一个单位继续处理。

## 注意事项

- **网络连接**：
  - 确保网络连接稳定，以减少重试次数和避免下载失败。
  
- **运行时间**：
  - 由于遍历的学号数量较多，下载过程可能耗时较长。建议在网络稳定的情况下运行该脚本。

- **存储空间**：
  - 照片文件会存储在 `photos` 文件夹中，请确保有足够的存储空间。

希望以上信息对您使用该脚本有所帮助！
