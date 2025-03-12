import asyncio

class Output:
    def __init__(self, parent=None, value=None, active=True, done=False):
        self.parent = parent
        self.active = active
        self.done = done
        self.value = value
        self.child = []

    def __call__(self):
        return self.value

    def __str__(self):
        return str(self.value)

    def __repr__(self):
        return str(self.value)

    def complete(self, value):
        self.value = value
        self.done = True

    def activate(self):
        self.active = True

    def activate_and_complete(self, value, parent):
        "Transform an optional result into a definite output"
        self.value = value
        self.parent = parent
        self.active = True
        self.done = True

    def deactivate(self):
        self.active = False

    def is_deactivated(self):
        if self.active:
            return False
        else:
            return True

    @property
    def val(self):
        return self.value


class Output_manager:
    def __init__(self):
        self.output_list = []

    def create_output_required(self, parent, value=None, active=True, done=False) -> Output:
        new_output = Output(parent, value, active, done)
        self.output_list.append(new_output)
        return new_output

    def create_output_optional(self, parent=None, value=None, active=False, done=False) -> Output:
        new_output = Output(parent, value, active, done)
        self.output_list.append(new_output)
        return new_output

    def create_output_complete(self, value, parent=None, active=True, done=True) -> Output:
        new_output = Output(parent, value, active, done)
        return new_output

    def run_all_outputs(self):
        "Execute all outputs recorded in self.output_list"
        for output in self.output_list:
            if output.is_deactivated():
                continue  # Skip this output
            if not output.parent:
                continue  # This output has no associated node
            if not output.done:
                # This output has not been executed; execute its parent node
                output.parent()
            else:
                # This output is already done; execute the next node
                for child in output.child:
                    child.run_chain()


class Output_manager_async:
    def __init__(self, semaphore: asyncio.Semaphore):
        self.output_list = []
        self.semaphore = semaphore

    def create_output_required(self, parent, value=None, active=True, done=False) -> Output:
        new_output = Output(parent, value, active, done)
        self.output_list.append(new_output)
        return new_output

    def create_output_optional(self, parent=None, value=None, active=False, done=False) -> Output:
        new_output = Output(parent, value, active, done)
        self.output_list.append(new_output)
        return new_output

    def create_output_complete(self, value, parent=None, active=True, done=True) -> Output:
        new_output = Output(parent, value, active, done)
        return new_output

    async def run_all_outputs(self):
        "Execute all outputs recorded in self.output_list"
        tasks_parent = []
        tasks_child = []
        for output in self.output_list:
            if output.is_deactivated():
                continue  # Skip this output
            if not output.parent:
                continue  # This output has no associated node
            if not output.done:
                # This output has not been executed; execute its parent node
                tasks_parent.append(self._task_run(output))
            else:
                # This output is already done; execute the next node
                tasks = [self._task_run_chain(child) for child in output.child]
                tasks_child = tasks_child + tasks

        await asyncio.gather(*tasks_parent)
        if tasks_child: await asyncio.gather(*tasks_child)


    async def _task_run(self, output):
        async with self.semaphore:
            await output.parent.run()  # 执行父节点

    async def _task_run_chain(self, child):
        async with self.semaphore:
            await child.run_chain()  # 执行字节点

