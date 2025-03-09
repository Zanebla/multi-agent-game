from core.agents import Role, Agent


def test_agent_prompt_generation():
    role = Role(name="软件工程师", expertise="后端开发", personality="严谨务实")
    agent = Agent(role)

    test_input = "我们需要设计一个像素小游戏"
    prompt = agent.generate_prompt(test_input)

    print("生成的提示：\n", prompt)
    assert "软件工程师" in prompt
    assert "后端开发" in prompt
    assert "严谨务实" in prompt
    print("✅ 角色提示词生成测试通过")


if __name__ == "__main__":
    test_agent_prompt_generation()
