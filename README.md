# FLOA
<span>
<img src=https://img.shields.io/badge/version-0.0.1-blue>
<img src=https://img.shields.io/badge/license-MIT-green>  
</span>


一个Python框架 , 用于快速搭建AI工作流 / A Python framework for quick building AI workflow.

---

### 项目结构
```
├── floa/               
│   ├── llm2dict.py     # 核心实现
│   ├── api.py          # 大模型API
│   ├── execute.py      # 执行生成的代码
│   ├── prompt.py       # 生成代码的提示词模版
│   └── validate.py     # 数据结构验证
```

---

## Output 
Output 类用于表示一个输出对象。它包含以下属性和方法：

#### 属性
- **parent**: 父节点，表示该输出的来源节点。

- **active**: 表示该输出(本对象)是否处于激活状态。

- **done**: 表示该输出(本对象)是否已完成。

- **value**: 输出的值，Output核心，整个对象就是为了管理这个值，这个值可以是任何类型的数据。

- **child**: 子节点列表，表示所有引用了这个输出值(Output.value)的下游节点。

#### 方法
- **\_\_init__(self, parent=None, value=None, active=True, done=False)**: 初始化输出对象。

- **\_\_call__(self)**: 返回输出值(Output.value)。

- **\_\_str__(self)**: 返回输出值(Output.value)的字符串表示。

- **\_\_repr__(self)**: 返回输出值(Output.value)的字符串表示。

- **complete(self, value)**: 标记输出对象完成并设置值。

- **activate(self)**: 激活输出对象(可用)。

- **activate_and_complete(self, value, parent)**: 激活输出对象可用并设置完成，同时设置父节点。

- **deactivate(self)**: 把输出对象标记为不可用。

- **is_deactivated(self)**: 输出对象是否为不可用。

- **val**: 属性，返回输出值(Output.done)。
----
## Output_manager
**Output_manager** 类用于管理输出(**Output**)对象。所有的 **Output** 对象都应该由 **Output_mansager** 创建。 它包含以下属性和方法：

#### 属性
**output_list**: 用于存储**Output**对象列表。

__init__(self): 初始化输出管理器。

- **create_output_required(self, parent, value=None, active=True, done=False) -> Output**: 创建一个必定有输出值的Output对象。节点计算完成后必定会对这个对象进行赋值(Output.value)，

- **create_output_optional(self, parent=None, value=None, active=False, done=False) -> Output**: 创建一个未激活的Output对象。节点执行完毕后决定不要不要激活这个Output，一般作为控制节点分支使用

- **create_output_complete(self, value, parent=None, active=True, done=True) -> Output**: 创建一个已完成的Output对象。一般作为常量使用

- **run_all_outputs(self)**: 执行所有记录在output_list的Output上游节点。执行所有节点

----

## Basic_node 
**Basic_node** 类是一个抽象基类，通过继承**Basic_node**实现具体的节点功能。它包含以下属性和方法：

#### 属性

- **om**: Output_manager的实例，用来新建和管理Output对象。

- **done**: 表示节点是否已完成计算。

- **active**: 表示节点是否处于激活状态。

- **list_output**: 节点输出对象列表。

- **list_input_verify**: 必填输入对象列表，执行节点前会确保该输入值已完成。

- **list_input_optional**: 可选输入对象列表，执行节点时会尝试执行可选输入。

- **dict_output**: 输出字典。值与list_output一致，多了输出对象的键值名称

- **dict_input**: 输入字典。值与list_input_verify和list_input_optional一致，多了输入对象的键值名称

- **retry_count**: 记录重试次数。

- **max_retries**: 最大重试次数。

#### 方法

- **\_\_init__(self, om: Output_manager, *args, \*\*kwargs)**: 初始化节点对象。

- **\_\_call__(self)**: 执行节点。

- **verify(self, *args: list[Output])**: 验证输入数据，如果上游节点没有执行会向上执行，直至所需的输入对象全部完成。

- **create_input_verify(self, value: Output)**: 创建一个输入对象，执行节点前会验证这个输入对象是已完成的，若该输入对象未完成，会执行该对象的上游节点。

- **create_input_optional(self, value: Output)**: 创建一个输入对象，节点执行时候，这个输入对象是可选的，即使这个输入对象未完成，也不会执行这个输入对象的上游节点。

- **create_output_required(self)**: 创建一个输出对象，节点执行完成后一定会对这个对象进行赋值并标记完成。

- **create_output_optional(self)**: 创建一个默认状态为未激活状态的输出对象，节点执行完成后根据具体情况来决定是否激活完成这个输出对象，通常用于节点分支，或可选输出。

- **run_chain(self)**: 链式执行，执行自身节点后会向下执行所有引用本节点输出(包含间接引用)的节点。

- **run(self)**: 执行本节点。

- **core(self)**: 抽象方法，继承本对象后，要编写具体实现的节点功能。

- **input(self)**: 抽象方法，继承本对象后，要编写具体的输入节点有哪些。

- **output(self)**: 抽象方法，继承本对象后，要编写具体的输出节点有哪些。

- **set_deactivate(self)**: 设置节点为失效状态。

- **set_complete(self)**: 设置节点为完成状态。

- **set_max_retries(self, max_retries: int)**: 设置执行节点(core)失败重试次数。

- **print(self, *args)**: 打印节点信息。

----