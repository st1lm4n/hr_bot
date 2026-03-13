import asyncio
from bot.utils.sheets import save_to_sheets


async def test():
    await save_to_sheets(
        telegram_id=123,
        full_name="Test User",
        username="testuser",
        answers=["ans1", "ans2", "ans3", "ans4", "ans5", "ans6", "http://example.com"],
        scores={"depth_score": 4, "critical_score": 5, "creativity_score": 4},
        total=13,
        hot=True,
    )


asyncio.run(test())
