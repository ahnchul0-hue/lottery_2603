import anthropic

from app.config import settings


def generate_reflection(
    machine: str,
    round_number: int,
    comparison_data: dict,
    past_reflections: list[str] | None = None,
) -> str:
    """Generate AI reflection memo from comparison results.

    Uses sync Anthropic client (consistent with project's sync endpoint pattern).
    Prompt is in Korean per Phase 5 D-09 (Korean UI).
    """
    if not settings.ANTHROPIC_API_KEY:
        raise ValueError("ANTHROPIC_API_KEY is not configured")

    client = anthropic.Anthropic(api_key=settings.ANTHROPIC_API_KEY)

    prompt = f"""당신은 로또 예측 분석가입니다. 다음 예측 결과를 분석하고 반성 메모를 한국어로 생성하세요.

호기: {machine}
회차: {round_number}

비교 결과 (JSON):
{comparison_data}

다음 항목을 포함하여 분석하세요:
1. 과대평가한 번호: 많이 예측했지만 당첨되지 않은 번호와 그 이유 추론
2. 누락한 번호 패턴: 당첨되었지만 예측하지 못한 번호의 특성 (구간, 홀짝, 고저 등)
3. 전략별 성과 분석: 어떤 전략이 잘 맞았고 어떤 전략이 부진했는지
4. 다음 예측을 위한 구체적 조정 제안: 가중치 변경, 주의할 번호대, 전략 활용 방안"""

    if past_reflections:
        recent = past_reflections[:3]  # Max 3 most recent per Research recommendation
        prompt += "\n\n과거 반성 메모 참고 (최근 3회):\n" + "\n---\n".join(recent)
        prompt += "\n\n위 과거 반성을 참고하여 반복되는 패턴이나 개선 사항을 반영하세요."

    message = client.messages.create(
        model=settings.REFLECTION_MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    return message.content[0].text
