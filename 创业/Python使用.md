日期： 2024-02-07

标签： #学习笔记 #技术

学习资料： 


---
<br>

### 搭建虚拟环境

```shell
# 1. 生成虚拟环境
python -m venv .venv

# 2. 激活虚拟环境
.venv\Scripts\activate

# 3. 生成环境依赖文件，并往里面编辑需要的依赖
pip freeze > requirements.txt

# 4. 安装依赖包
pip install -r requirements.txt
```
