# 测试指南

本项目的单元测试使用 pytest 框架编写。

## 运行测试

### 运行所有测试
```bash
pytest
```

### 运行特定测试文件
```bash
pytest tests/test_utils.py
pytest tests/test_visualize.py
pytest tests/test_main.py
```

### 运行特定测试类或方法
```bash
pytest tests/test_utils.py::TestCleanAmount
pytest tests/test_utils.py::TestCleanAmount::test_clean_normal_amount
```

### 查看详细输出
```bash
pytest -v
```

### 查看代码覆盖率
```bash
pytest --cov=.
pytest --cov=. --cov-report=html
```

### 运行测试并显示 print 输出
```bash
pytest -s
```

## 测试结构

```
tests/
├── __init__.py           # 测试包初始化
├── conftest.py           # pytest 配置和共享 fixtures
├── test_utils.py         # utils.py 模块的测试
├── test_visualize.py     # visualize.py 模块的测试
└── test_main.py          # main.py 模块的测试
```

## 编写新测试

1. 在相应的测试文件中添加测试类
2. 使用 pytest fixtures (在 conftest.py 中定义)
3. 遵循命名规范：测试函数以 `test_` 开头
4. 使用清晰的断言

示例：
```python
def test_new_feature(sample_df):
    """测试新功能"""
    result = new_function(sample_df)
    assert result is not None
    assert len(result) > 0
```

## 测试覆盖率目标

- 整体代码覆盖率目标：70%+
- 核心功能模块（utils.py, visualize.py）：80%+

## 注意事项

- 某些测试被标记为 `@pytest.mark.skip`，因为它们需要实际的 PDF/ZIP 文件
- 测试使用临时目录（temp_dir fixture）来避免污染项目文件
- mock 用于模拟外部依赖（如文件 I/O 操作）