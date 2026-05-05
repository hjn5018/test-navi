import asyncio
import os
from loguru import logger
from dotenv import load_dotenv

# 환경 변수 로드
load_dotenv()

from app.models.schemas import AgentRequest
from app.services.llm_service import LLMFactory
from app.services.automation_service import AutomationService, PlaywrightBrowserService

async def main():
    logger.info("유튜브 검색 및 재생 E2E 시나리오 시작")
    
    # 1. LLM 에이전트 초기화
    llm_service = LLMFactory.get_service()
    
    # 2. 사용자 입력
    user_input = "유튜브에서 '뉴진스' 검색해서 첫 번째 영상 틀어줘"
    logger.info(f"사용자 입력: {user_input}")
    
    # 3. LLM으로 액션 생성
    logger.info("LLM으로 브라우저 액션 생성 중...")
    req = AgentRequest(text=user_input)
    res = await llm_service.process(req)
    
    logger.info("생성된 액션 목록:")
    for i, action in enumerate(res.actions):
        logger.info(f"  [{i+1}] {action.action} -> {action.params}")
        
    if not res.actions:
        logger.error("액션이 생성되지 않았습니다.")
        return
        
    # 4. 자동화 엔진으로 액션 실행
    logger.info("자동화 엔진 시작 (브라우저 노출: headless=False)")
    # 데모를 위해 화면에 보이게 실행
    browser_service = PlaywrightBrowserService(headless=False)
    automation_service = AutomationService(browser_service=browser_service)
    
    try:
        results = await automation_service.execute_actions("e2e_demo", res.actions)
        
        success_count = sum(1 for r in results if r.success)
        logger.info(f"실행 완료: {success_count}/{len(res.actions)} 액션 성공")
        
        # 결과를 볼 수 있도록 잠시 대기
        logger.info("실행 결과를 확인하기 위해 5초 대기합니다...")
        await asyncio.sleep(5)
        
    except Exception as e:
        logger.exception("실행 중 오류 발생")
    finally:
        logger.info("브라우저 정리 중...")
        await automation_service.cleanup()
        logger.info("완료")

if __name__ == "__main__":
    asyncio.run(main())
