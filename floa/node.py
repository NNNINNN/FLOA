from .output import Output, Output_manager
from abc import ABC, abstractmethod
import asyncio


class Basic_node(ABC):
    def __init__(self, om: Output_manager, *args, **kwargs):
        self.om = om
        self.done = False  # 记录节点已完成计算
        self.active = True
        self.list_output = []  # 节点输出 必定输出和可能输出都包括在里面
        self.list_input_verify = []  # 必填输入, 执行本节点前会确保该输入值以完成, 若设定的输入无效, 则本节点执行失败
        self.list_input_optional = []  # 可选输入, 执行本节点时, 会尝试执行可多选输入, 若可选输入无效, 则会跳过
        self.dict_output = {}
        self.dict_input = {}
        if args:
            self.input(*args)
        if kwargs:
            self.input(**kwargs)
        self.output()
        self.retry_count = 0  # 记录重试次数
        self.max_retries = 3  # 最大重试次数
        self.name = None

    def __call__(self):
        # *1* 检验节点
        if self.done:
            # self.print("节点已完成计算")
            return True
        if not self.active:
            # self.print("节点已失效")
            return False
        # *2* 检验输入参数 重要:如果输入的上级节点没有执行过,将会被执行
        验证结果 = self.verify(*self.list_input_verify)
        if not 验证结果:
            self.print("运行失败 verify输入参数验证失败")
            return False
        # *3* 本节点功能的具体实现 根据运行结果标记节点
        if self.core():
            self.set_complete()
            return True
        else:
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                self.set_deactivate()
                return False
            else:
                self.print(f"core() 失败，正在重试 ({self.retry_count}/{self.max_retries})")
                return self.__call__()  # 递归调用自身进行重试

    def verify(self, *args: list[Output]):
        "验证输入数据, 如果没有通过, 执行上方的节点 parent()"
        for output in args:
            if output.done == True:  # 这个输出已计算完毕 跳过
                continue
            elif output.done == False:
                if not output.parent:  # 这个输出没有所属节点（父）
                    self.print("verify 输入验证失败")
                    return False
                output.parent()  # 运行上级节点
        return True

    def create_input_verify(self, value: Output):
        if not isinstance(value, Output):
            value = self.om.create_output_complete(value)
        value.child.append(self)
        self.list_input_verify.append(value)
        return value

    def create_input_optional(self, value: Output):
        if not isinstance(value, Output):
            value = self.om.create_output_complete(value)
        value.child.append(self)
        self.list_input_optional.append(value)
        return value

    def create_output_required(self):
        op = self.om.create_output_required(self)
        self.list_output.append(op)
        return op

    def create_output_optional(self):
        op = self.om.create_output_optional()
        self.list_output.append(op)
        return op

    def run_chain(self):
        "对有效输出向下执行节点"
        self.__call__()
        # print(self.list_output)
        for output in self.list_output:
            if output.is_deactivated(): continue  # 已关闭的分支 跳过
            if output.child:
                for child in output.child:
                    child.run_chain()  # 注意

    def run(self):
        self.__call__()

    @abstractmethod
    def core(self):
        pass

    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def output(self):
        pass

    def set_deactivate(self):
        self.active = False
        self.done = False

    def set_complete(self):
        self.done = True

    def set_max_retries(self, max_retries: int):
        "设置节点失败重试"
        self.max_retries = max_retries

    def print(self, *args):
        if self.name:
            print(f"节点{self.name}:", *args)
        else:
            print(*args)


class Basic_node_async(ABC):
    def __init__(self, om: Output_manager, semaphore: asyncio.Semaphore, *args, **kwargs):
        self.om = om
        self.semaphore = semaphore
        self.done = False  # 记录节点已完成计算
        self.active = True
        self.list_output = []  # 节点输出 必定输出和可能输出都包括在里面
        self.list_input_verify = []  # 必填输入, 执行本节点前会确保该输入值以完成, 若设定的输入无效, 则本节点执行失败
        self.list_input_optional = []  # 可选输入, 执行本节点时, 会尝试执行可多选输入, 若可选输入无效, 则会跳过
        self.dict_output = {}
        self.dict_input = {}
        if args:
            self.input(*args)
        if kwargs:
            self.input(**kwargs)
        self.output()
        self.retry_count = 0  # 记录重试次数
        self.max_retries = 3  # 最大重试次数
        self.name = None

    async def __call__(self):
        # *1* 检验节点
        if self.done:
            # self.print("本节点已完成计算")
            return True
        if not self.active:
            # self.print("本节点已失效")
            return False
        # *2* 检验输入参数 重要:如果输入的上级节点没有执行过,将会被执行
        验证结果 = await self.verify(*self.list_input_verify)
        if not 验证结果:
            self.print("运行失败 verify输入参数验证失败")
            return False
        # *3* 本节点功能的具体实现 根据运行结果标记节点
        if await self.core():
            self.set_complete()
            return True
        else:
            self.retry_count += 1
            if self.retry_count >= self.max_retries:
                self.set_deactivate()
                return False
            else:
                self.print(f"core() 失败，正在重试 ({self.retry_count}/{self.max_retries})")
                return await self.__call__()  # 递归调用自身进行重试

    async def verify(self, *args: list[Output]):
        "验证输入数据, 如果没有通过, 执行上方的节点 parent()"
        tasks = []
        for output in args:
            if output.done == True:  # 这个输出已计算完毕 跳过
                continue
            elif output.done == False:
                if not output.parent:  # 这个输出没有所属节点（父）
                    self.print("verify 输入验证失败")
                    return False
                tasks.append(self.task_run_parent(output))
                # output.parent()  # 运行上级节点
        self.semaphore.release()  # 可用线程数+1 本组可用线程+1 防主线程消耗完所有线程数
        await asyncio.gather(*tasks)
        await self.semaphore.acquire()  # 可用线程数+1
        return True

    async def task_run_parent(self, output):
        async with self.semaphore:
            await output.parent()  # 执行节点

    async def task_run_chain(self, child):
        async with self.semaphore:
            # print(f"task_run_chain")
            await child.run_chain()  # 模拟耗时操作

    def create_input_verify(self, value: Output):
        if not isinstance(value, Output):
            value = self.om.create_output_complete(value)
        value.child.append(self)
        self.list_input_verify.append(value)
        return value

    def create_input_optional(self, value: Output):
        if not isinstance(value, Output):
            value = self.om.create_output_complete(value)
        value.child.append(self)
        self.list_input_optional.append(value)
        return value

    def create_output_required(self):
        op = self.om.create_output_required(self)
        self.list_output.append(op)
        return op

    def create_output_optional(self):
        op = self.om.create_output_optional()
        self.list_output.append(op)
        return op

    async def run_chain(self):
        "对有效输出向下执行节点"
        await self.__call__()
        # print(self.list_output)
        tasks = []
        for output in self.list_output:
            if output.is_deactivated(): continue  # 已关闭的分支 跳过
            if output.child:
                # print("run_chain:", " child:", len(output.child), output.child)
                for child in output.child:
                    tasks.append(self.task_run_chain(child))
        self.semaphore.release()  # 可用线程数+1 本组可用线程+1 防主线程消耗完所有线程数
        await asyncio.gather(*tasks)
        await self.semaphore.acquire()  # 可用线程数-1

    async def run(self):
        await self.__call__()

    @abstractmethod
    async def core(self):
        pass

    @abstractmethod
    def input(self):
        pass

    @abstractmethod
    def output(self):
        pass

    def set_deactivate(self):
        self.active = False
        self.done = False

    def set_complete(self):
        self.done = True

    def set_max_retries(self, max_retries: int):
        "设置节点失败重试"
        self.max_retries = max_retries

    def print(self, *args):
        if self.name:
            print(f"节点{self.name}:", *args)
        else:
            print(*args)
