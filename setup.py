from setuptools import setup, find_packages
from os import path

this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setup(
    name='floa',  # 包名，必须唯一
    version='0.0.1',  # 版本号
    author='NNNINNN',  # 作者名
    author_email='jianningwork@outlook.com',  # 作者邮箱
    description='Quick building AI workflow.',  # 包的简短描述
    long_description=long_description,  # 包的详细描述（从 README.md 读取）
    long_description_content_type='text/markdown',  # 指定详细描述的格式为 Markdown
    url='https://github.com/NNNINNN/FLOA',  # 项目地址
    packages=find_packages(),  # 自动查找包中的模块
    install_requires=[
        # 列出依赖包
    ],  # 定义包的依赖项
    classifiers=[
        'Programming Language :: Python :: 3',  # 支持的 Python 版本
        'License :: OSI Approved :: MIT License',  # 许可证类型
        'Operating System :: OS Independent',  # 支持的操作系统
    ],  # 分类信息，用于在 PyPI 上分类显示
    python_requires='>=3.6',  # 指定支持的最低 Python 版本
)