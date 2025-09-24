from setuptools import setup, find_packages

setup(
    name="your-package-name",
    version="0.1.0",
    # 明确指定要在哪个目录下查找包，并排除不需要的目录
    packages=find_packages(where="src", exclude=["tests*"]),
    # 告诉 setuptools 包所在的目录
    package_dir={"": "src"},
    # ... 其他元数据（install_requires 等）...
)