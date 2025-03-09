from core.tasks import TaskTree


def test_task_tree():
    # 初始化任务树
    project = TaskTree("开发像素风小游戏")

    # 添加子任务
    dev_task_id = project.add_subtask("T0", "后端API开发", "后端工程师")
    ui_task_id = project.add_subtask("T0", "用户界面设计", "UI设计师")

    # 验证任务数量
    assert len(project.tasks) == 3
    # 验证父子关系
    assert dev_task_id in project.tasks["T0"].children
    print("任务树结构验证通过！")


if __name__ == "__main__":
    test_task_tree()
