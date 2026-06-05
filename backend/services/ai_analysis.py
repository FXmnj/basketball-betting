"""
AI Analysis Service using OpenAI GPT-5.2
Generates natural language match analysis and insights
"""
import os
from typing import Dict, List, Optional
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass
class AnalysisResult:
    match_id: str
    summary: str
    key_insights: List[str]
    prediction_reasoning: str
    risk_assessment: str
    betting_angle: str


class AIAnalysisService:
    """
    AI-powered analysis service using GPT-5.2.
    Generates human-readable match analysis.
    """
    
    def __init__(self):
        self.api_key = os.environ.get("EMERGENT_LLM_KEY")
        self.model = "gpt-5.2"
    
    async def generate_match_analysis(
        self,
        match_data: Dict,
        prediction_data: Dict,
        include_betting_analysis: bool = True
    ) -> AnalysisResult:
        """
        Generate comprehensive match analysis using AI.
        """
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        # Build context for the AI
        home_team = match_data.get("home_team_name", "Home Team")
        away_team = match_data.get("away_team_name", "Away Team")
        league = match_data.get("league_name", "League")
        
        home_prob = prediction_data.get("home_win_prob", 33)
        draw_prob = prediction_data.get("draw_prob", 33)
        away_prob = prediction_data.get("away_win_prob", 33)
        
        expected_home = prediction_data.get("expected_home_goals", 1.5)
        expected_away = prediction_data.get("expected_away_goals", 1.2)
        
        value_bets = prediction_data.get("value_bets", [])
        
        prompt = f"""You are an expert football analyst providing match preview analysis.

Match: {home_team} vs {away_team}
Competition: {league}

Model Predictions:
- {home_team} Win: {home_prob}%
- Draw: {draw_prob}%
- {away_team} Win: {away_prob}%
- Expected Goals: {home_team} {expected_home}, {away_team} {expected_away}

Value Bets Identified: {len(value_bets)}
{chr(10).join([f"- {vb.get('selection', 'N/A')}: {vb.get('edge', 0)}% edge at odds {vb.get('odds', 0)}" for vb in value_bets[:3]])}

Provide a concise analysis including:
1. A 2-3 sentence match preview summary
2. 3 key insights (bullet points)
3. Brief prediction reasoning (2 sentences)
4. Risk assessment (Low/Medium/High with 1 sentence explanation)
5. Best betting angle if any value bets exist

Keep the response professional and data-driven. Be direct and avoid filler phrases."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id=f"match_analysis_{match_data.get('id', 'unknown')}",
                system_message="You are an expert football analyst specializing in statistical analysis and match predictions. Provide concise, data-driven insights."
            ).with_model("openai", self.model)
            
            user_message = UserMessage(text=prompt)
            response = await chat.send_message(user_message)
            
            # Parse the response
            return self._parse_analysis_response(
                match_data.get("id", ""),
                response
            )
            
        except Exception:
            # Fallback to template-based analysis
            return self._generate_fallback_analysis(
                match_data, prediction_data
            )
    
    def _parse_analysis_response(
        self,
        match_id: str,
        response: str
    ) -> AnalysisResult:
        """Parse AI response into structured format."""
        lines = response.strip().split('\n')
        
        summary = ""
        insights = []
        reasoning = ""
        risk = ""
        betting = ""
        
        current_section = None
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            if "summary" in line.lower() or "preview" in line.lower():
                current_section = "summary"
            elif "insight" in line.lower() or "key" in line.lower():
                current_section = "insights"
            elif "reasoning" in line.lower() or "prediction" in line.lower():
                current_section = "reasoning"
            elif "risk" in line.lower():
                current_section = "risk"
            elif "betting" in line.lower() or "angle" in line.lower():
                current_section = "betting"
            elif line.startswith(('-', '•', '*')):
                if current_section == "insights":
                    insights.append(line.lstrip('-•* '))
            else:
                if current_section == "summary":
                    summary += line + " "
                elif current_section == "reasoning":
                    reasoning += line + " "
                elif current_section == "risk":
                    risk += line + " "
                elif current_section == "betting":
                    betting += line + " "
        
        # If parsing didn't work well, use the whole response
        if not summary and not insights:
            parts = response.split('\n\n')
            summary = parts[0] if parts else response[:200]
            insights = [response[200:400]] if len(response) > 200 else []
        
        return AnalysisResult(
            match_id=match_id,
            summary=summary.strip() or "Analysis not available.",
            key_insights=insights[:5] if insights else ["Check prediction probabilities for insights."],
            prediction_reasoning=reasoning.strip() or "Based on statistical model analysis.",
            risk_assessment=risk.strip() or "Medium - Standard match volatility.",
            betting_angle=betting.strip() or "Review value bets for opportunities."
        )
    
    def _generate_fallback_analysis(
        self,
        match_data: Dict,
        prediction_data: Dict
    ) -> AnalysisResult:
        """Generate analysis without AI when API fails."""
        home = match_data.get("home_team_name", "Home")
        away = match_data.get("away_team_name", "Away")
        
        home_prob = prediction_data.get("home_win_prob", 33)
        away_prob = prediction_data.get("away_win_prob", 33)
        expected_goals = prediction_data.get("expected_home_goals", 1.5) + prediction_data.get("expected_away_goals", 1.2)
        
        # Determine summary based on favorites
        if home_prob > 50:
            summary = f"{home} enters as favorites at home with a {home_prob}% win probability."
        elif away_prob > 40:
            summary = f"{away} has strong away chances at {away_prob}% despite playing away."
        else:
            summary = f"This match looks evenly contested between {home} and {away}."
        
        insights = [
            f"Expected total goals: {expected_goals:.1f}",
            f"Model confidence in prediction: {prediction_data.get('confidence', 70)}%",
            f"BTTS probability: {prediction_data.get('btts_prob', 50)}%"
        ]
        
        value_bets = prediction_data.get("value_bets", [])
        if value_bets:
            insights.append(f"{len(value_bets)} value bet(s) identified with positive edge")
        
        return AnalysisResult(
            match_id=match_data.get("id", ""),
            summary=summary,
            key_insights=insights,
            prediction_reasoning="Based on Poisson, ML ensemble, and Monte Carlo simulation models.",
            risk_assessment="Medium - Standard match prediction risk.",
            betting_angle=f"Best value: {value_bets[0].get('selection', 'N/A')}" if value_bets else "No clear value bets identified."
        )
    
    async def generate_daily_summary(
        self,
        matches: List[Dict],
        predictions: List[Dict]
    ) -> str:
        """Generate daily betting summary."""
        from emergentintegrations.llm.chat import LlmChat, UserMessage
        
        total_value_bets = sum(len(p.get("value_bets", [])) for p in predictions)
        avg_confidence = sum(p.get("confidence", 70) for p in predictions) / len(predictions) if predictions else 70
        
        prompt = f"""Generate a brief daily football betting summary:

Today's Matches: {len(matches)}
Value Bets Found: {total_value_bets}
Average Model Confidence: {avg_confidence:.1f}%

Top 3 matches by confidence:
{chr(10).join([f"- {p.get('home_team', 'Home')} vs {p.get('away_team', 'Away')}: {p.get('confidence', 70)}% confidence" for p in sorted(predictions, key=lambda x: x.get('confidence', 0), reverse=True)[:3]])}

Provide a 3-sentence summary of today's betting outlook."""

        try:
            chat = LlmChat(
                api_key=self.api_key,
                session_id="daily_summary",
                system_message="You are a professional sports betting analyst."
            ).with_model("openai", self.model)
            
            response = await chat.send_message(UserMessage(text=prompt))
            return response
            
        except Exception:
            return f"Today features {len(matches)} matches with {total_value_bets} value betting opportunities identified. Average model confidence stands at {avg_confidence:.1f}%."
