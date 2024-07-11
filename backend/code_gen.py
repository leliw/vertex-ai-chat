from pathlib import Path
from ai_agents import AICodeFileAgent


agent = AICodeFileAgent(
    "gemini-1.5-flash",
    "Jesteś ekspertem od kodwania Python3.12. Standardowo korzystasz z bibliotek FastAPI i Pydantic.",
)

ret = agent.run_and_save_files(
    prompt="""
    Zaimplementuj CRUD do zarządzania użytkownikami systemu.
    Stwórz model User, serwis UserService i router UsersRouter wg wzorca poniżej
    """,
    input_files=[
        Path("app/routers/agents.py"),
        Path("app/agent/agent_model.py"),
        Path("app/agent/agent_service.py"),
    ],
    output_dir=Path("out"),
)

print("===")
print(ret)
