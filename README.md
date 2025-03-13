![Issue Image](readme/logo.png)  

<span>
<img src=https://img.shields.io/badge/version-0.0.1-blue>
<img src=https://img.shields.io/badge/license-MIT-green>  
</span>


FLOA是一个Python框架 , 用于快速搭建AI工作流 / A Python framework for quick building AI workflow.

---

### 安装与使用

```shell
pip install floa
```

### 例子
![Issue Image](readme/Example_1.png)
```python
from floa import Output_manager, Basic_node
import random


class RandomNum_node(Basic_node):
    "随机节点"

    def input(self):
        pass

    def output(self):
        self.o_num = self.create_output_required()

    def core(self):
        self.o_num.complete(random.random()*10)
        print("随机数节点输出:", self.o_num.value)
        return True

class Add_node(Basic_node):
    "加法节点"

    def input(self, a, b):
        self.i_a = self.create_input_verify(a)
        self.i_b = self.create_input_verify(b)

    def output(self):
        self.o_sum = self.create_output_required()
        self.o_sum_int = self.create_output_required()

    def core(self):
        o_sum = self.i_a.value + self.i_b.value
        o_sum_int = int(o_sum)
        self.o_sum.complete(o_sum)
        self.o_sum_int.complete(o_sum_int)
        print(f"加法节点输出,o_sum:{self.o_sum},o_sum_int:{self.o_sum_int}")
        return True

class Branch_node(Basic_node):
    "分支节点"

    def input(self, num_int):
        self.i_num_int = self.create_input_verify(num_int)

    def output(self):
        self.o_odd = self.create_output_optional()  # 奇数
        self.o_even = self.create_output_optional()  # 偶数

    def core(self):
        num = int(self.i_num_int.value)
        if num % 2 == 0:
            self.o_even.activate_and_complete(num,self)
        else:
            self.o_odd.activate_and_complete(num,self)
        print(f"奇偶分支节点输出,o_odd:{self.o_odd},o_even:{self.o_even}")
        return True

class Loop_node(Basic_node):
    "循环节点"

    def input(self, num_int):
        self.i_num_int = self.create_input_verify(num_int)

    def output(self):
        self.o_random_sum = self.create_output_required()

    def core(self):
        _om = Output_manager()
        o_random_sum = 0
        print("循环----")
        for i in range(self.i_num_int.value):
            _n1 = RandomNum_node(_om)
            _n2 = RandomNum_node(_om)
            _n3 = Add_node(_om)
            _n3.input(_n1.o_num, _n2.o_num)
            _n3.run()
            o_random_sum += _n1.o_num.value
        print("循环----")
        self.o_random_sum.complete(o_random_sum)
        return True

class Text_node(Basic_node):
    "文本节点"

    def input(self, t):
        self.i_t = self.create_input_verify(t)
    def output(self):
        pass
    def core(self):
        print(f"奇数,没有进入循环,{self.i_t.value}")
        return True

om = Output_manager()

n1 = RandomNum_node(om)
n2 = RandomNum_node(om)
n3 = Add_node(om)
n4 = Branch_node(om)
n5 = Loop_node(om)
n6 = Text_node(om)

n3.input(n1.o_num, n2.o_num)
n4.input(n3.o_sum_int)
n5.input(n4.o_even)
n6.input(n4.o_odd)

n1.run_chain()

```
返回（奇数情况）：
```
随机数节点输出: 0.7183263256552752
随机数节点输出: 9.778909838547282
加法节点输出,o_sum:10.497236164202556,o_sum_int:10
奇偶分支节点输出,o_odd:None,o_even:10
循环----
随点输出: 9.575348349989815
随机数节点输出: 9.65215113676025
加法节点输出,o_sum:19.227499486750062,o_sum_int:19
<...省略...>
随机数节点输出: 1.8791804643619792
随机数节点输出: 0.14144630166600836
加法节点输出,o_sum:3.2115728227046025,o_sum_int:3
循环----
```
返回（偶数情况）：
```
随机数节点输出: 8.260669282639027
随机数节点输出: 6.796344337173669
加法节点输出,o_sum:15.057013619812697,o_sum_int:15
奇偶分支节点输出,o_odd:15,o_even:None
奇数,没有进入循环,15
```

### 项目结构
```
floa/               
├── output.py    # 输出值对象
└── node.py      # 基础节点
```

**Output** 对象核心是管理一个 "值" -> Output.value，以及这个值的上下游节点的关系

```python
from floa import Output
o = Output()
print("创建时 o.value 默认值为:",o.value)
o.complete(10) #赋值
print("上游节点有运行结果后对o使用o.complete(10)进行赋值o.value:",o.value,)
```
输出
```
创建时 o.value 默认值为: None
上游节点有运行结果后对o使用o.complete(10)进行赋值o.value: 10
```

一般情况我们都不用Output创建输出对象，而是使用**Output_manager**对象创建，用它管理一个工作流的Output

```python
from floa import Output_manager

om = Output_manager()

o = om.create_output_complete(10)
print("[常量] om.create_output_complete创建了一个上游节点已完成运算的输出,可以把它看成一个常量:",o.value,"\n")

o = om.create_output_required(object)
print("[必定输出] om.create_output_required创建并绑定上游节点",o.value)
o.complete(10)
print("上游节点运算完成后, 一定会对o进行赋值,使用:o.complete(10):",o.value,"\n")

o = om.create_output_optional()
print("[可选输出] 使用om.create_output_optional创建一个不激活的输出,节点运算完后有可能输出分支时候使用:",o.value)
o.activate_and_complete(10,object)
print("使用activate_and_complete进行赋值激活:",o.value)
```
输出
```
[常量] om.create_output_complete创建了一个上游节点已完成运算的输出,可以把它看成一个常量: 10 

[必定输出] om.create_output_required创建并绑定上游节点 None
上游节点运算完成后, 一定会对o进行赋值,使用:o.complete(10): 10

[可选输出] 使用om.create_output_optional创建一个不激活的输出,节点运算完后有可能输出分支时候使用: None
使用activate_and_complete进行赋值激活: 10
```

**Basic_node** 是所有节点的基类。你可以通过继承它来定义输入输出（input/output），然后在 core 里写代码，实现具体的节点功能。

```python
from floa import Basic_node, Output_manager

class x2node(Basic_node):

    def input(self, n):
        self.n = self.create_input_verify(n)

    def output(self):
        self.output_nx2 = self.create_output_required()

    def core(self) -> bool:
        nx2 = self.n.value * 2
        self.output_nx2.complete(nx2)
        return True

om = Output_manager()
n1 = x2node(om)
n2 = x2node(om,n1.output_nx2)
n3 = x2node(om,n2.output_nx2)

n1.input(3)
n1.run_chain()
print(f"n1输出:{n1.output_nx2}，n2输出:{n2.output_nx2}，n3输出:{n3.output_nx2}")
```
输出
```
n1输出:6，n2输出:12，n3输出:24
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