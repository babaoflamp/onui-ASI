import sqlite3
import json
import logging
from typing import List, Dict, Any
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class AnalyticsService:
    def __init__(self, db_path: str = "data/users.db"):
        self.db_path = db_path

    def _get_connection(self):
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def get_user_weakness_report(self, user_id: int) -> Dict[str, Any]:
        """사용자의 학습 데이터를 분석하여 약점 리포트를 생성합니다."""
        conn = self._get_connection()
        try:
            cursor = conn.cursor()
            
            # 1. 취약한 문장 분석 (최근 점수가 70점 미만인 항목)
            cursor.execute("""
                SELECT sentence_id, sentence_text, level, score_latest, accuracy_latest, attempt_count
                FROM sentence_scores
                WHERE user_id = ? AND score_latest < 70
                ORDER BY score_latest ASC
                LIMIT 5
            """, (user_id,))
            weak_sentences = [dict(row) for row in cursor.fetchall()]

            # 2. 취약한 단어 분석 (평균 점수가 낮은 단어)
            cursor.execute("""
                SELECT word_id, AVG(score) as avg_score, COUNT(*) as count
                FROM word_score_history
                WHERE user_id = ?
                GROUP BY word_id
                HAVING avg_score < 70
                ORDER BY avg_score ASC
                LIMIT 5
            """, (user_id,))
            weak_words = [dict(row) for row in cursor.fetchall()]

            # 3. 학습 패턴 분석 (최근 7일간의 학습 횟수)
            seven_days_ago = (datetime.now() - timedelta(days=7)).isoformat()
            cursor.execute("""
                SELECT COUNT(*) as total_attempts
                FROM sentence_score_history
                WHERE user_id = ? AND created_at > ?
            """, (user_id, seven_days_ago))
            recent_activity = cursor.fetchone()["total_attempts"]

            # 4. 발음 오류 패턴 분석 (실제 SpeechPro 상세 데이터가 있으면 더 고도화 가능)
            # 여기서는 예시로 가장 점수가 낮은 레벨을 추출
            cursor.execute("""
                SELECT level, AVG(score_latest) as avg_score
                FROM sentence_scores
                WHERE user_id = ?
                GROUP BY level
                ORDER BY avg_score ASC
                LIMIT 1
            """, (user_id,))
            weakest_level_row = cursor.fetchone()
            weakest_level = weakest_level_row["level"] if weakest_level_row else "N/A"

            return {
                "user_id": user_id,
                "generated_at": datetime.now().isoformat(),
                "weak_sentences": weak_sentences,
                "weak_words": weak_words,
                "recent_activity_count": recent_activity,
                "weakest_level": weakest_level,
                "summary": self._generate_summary(weak_sentences, weak_words)
            }
        except Exception as e:
            logger.error(f"Failed to generate weakness report: {e}")
            return {"error": str(e)}
        finally:
            conn.close()

    def _generate_summary(self, sentences: list, words: list) -> str:
        if not sentences and not words:
            return "아직 충분한 학습 데이터가 없습니다. 더 많은 문장과 단어를 연습해 보세요!"
        
        msg = f"최근 학습에서 {len(sentences)}개의 문장과 {len(words)}개의 단어에서 개선이 필요한 것으로 나타났습니다. "
        if sentences:
            msg += f"특히 '{sentences[0]['sentence_text']}'와 같은 문장의 발음을 집중적으로 연습해 보세요."
        return msg
