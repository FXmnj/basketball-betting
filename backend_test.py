import requests
import sys
import json
from datetime import datetime, date

class FootballPredictionAPITester:
    def __init__(self, base_url="https://betting-quant.preview.emergentagent.com"):
        self.base_url = base_url
        self.tests_run = 0
        self.tests_passed = 0
        self.failed_tests = []

    def run_test(self, name, method, endpoint, expected_status, data=None, timeout=30):
        """Run a single API test"""
        url = f"{self.base_url}/api{endpoint}"
        headers = {'Content-Type': 'application/json'}

        self.tests_run += 1
        print(f"\n🔍 Testing {name}...")
        print(f"   URL: {url}")
        
        try:
            if method == 'GET':
                response = requests.get(url, headers=headers, timeout=timeout)
            elif method == 'POST':
                response = requests.post(url, json=data, headers=headers, timeout=timeout)

            success = response.status_code == expected_status
            if success:
                self.tests_passed += 1
                print(f"✅ Passed - Status: {response.status_code}")
                try:
                    response_data = response.json()
                    print(f"   Response keys: {list(response_data.keys()) if isinstance(response_data, dict) else 'Non-dict response'}")
                    return True, response_data
                except:
                    return True, response.text
            else:
                print(f"❌ Failed - Expected {expected_status}, got {response.status_code}")
                print(f"   Response: {response.text[:200]}...")
                self.failed_tests.append({
                    "test": name,
                    "endpoint": endpoint,
                    "expected": expected_status,
                    "actual": response.status_code,
                    "response": response.text[:500]
                })
                return False, {}

        except requests.exceptions.Timeout:
            print(f"❌ Failed - Timeout after {timeout}s")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": "Timeout"
            })
            return False, {}
        except Exception as e:
            print(f"❌ Failed - Error: {str(e)}")
            self.failed_tests.append({
                "test": name,
                "endpoint": endpoint,
                "error": str(e)
            })
            return False, {}

    def test_health_endpoints(self):
        """Test basic health and root endpoints"""
        print("\n" + "="*50)
        print("TESTING HEALTH ENDPOINTS")
        print("="*50)
        
        self.run_test("API Root", "GET", "/", 200)
        self.run_test("Health Check", "GET", "/health", 200)
        self.run_test("API Status", "GET", "/admin/api-status", 200)

    def test_dashboard_endpoints(self):
        """Test dashboard related endpoints"""
        print("\n" + "="*50)
        print("TESTING DASHBOARD ENDPOINTS")
        print("="*50)
        
        success, stats_data = self.run_test("Dashboard Stats", "GET", "/dashboard/stats", 200)
        if success:
            required_keys = ["total_matches_today", "total_value_bets", "avg_edge", "model_accuracy_7d", "api_football_configured"]
            missing_keys = [key for key in required_keys if key not in stats_data]
            if missing_keys:
                print(f"   ⚠️  Missing keys in stats: {missing_keys}")
            else:
                print(f"   ✅ All required stats keys present")

    def test_matches_endpoints(self):
        """Test match related endpoints"""
        print("\n" + "="*50)
        print("TESTING MATCHES ENDPOINTS")
        print("="*50)
        
        # Test daily matches
        success, matches_data = self.run_test("Get Daily Matches", "GET", "/daily-matches", 200)
        match_id = None
        
        if success and isinstance(matches_data, dict):
            matches = matches_data.get("matches", [])
            total_matches = matches_data.get("total_matches", 0)
            print(f"   ✅ Found {total_matches} matches for today")
            
            if matches:
                match = matches[0]
                match_id = match.get("id") or match.get("external_id")
                required_fields = ["home_team_name", "away_team_name", "league_name", "kickoff"]
                missing_fields = [field for field in required_fields if field not in match]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in match: {missing_fields}")
                else:
                    print(f"   ✅ Match structure looks good")
        
        # Test match detail if we have a match ID
        if match_id:
            self.run_test("Get Match Detail", "GET", f"/matches/{match_id}", 200)
            
            # Test AI analysis (might take longer due to AI call)
            print(f"\n🧠 Testing AI Analysis - this may take 10-15 seconds...")
            self.run_test("Get Match Analysis", "GET", f"/matches/{match_id}/analysis", 200, timeout=45)

    def test_predictions_endpoints(self):
        """Test prediction endpoints - MAIN FEATURE"""
        print("\n" + "="*50)
        print("TESTING PREDICTIONS ENDPOINTS")
        print("="*50)
        
        # Test daily predictions - main endpoint
        success, pred_data = self.run_test("Get Daily Predictions", "GET", "/daily-predictions", 200)
        if success and isinstance(pred_data, dict):
            predictions = pred_data.get("predictions", [])
            total_predictions = pred_data.get("total_predictions", 0)
            data_source = pred_data.get("data_source", "unknown")
            print(f"   ✅ Found {total_predictions} predictions")
            print(f"   📊 Data source: {data_source}")
            
            if predictions:
                prediction = predictions[0]
                # Check prediction structure
                required_fields = ["match_id", "home_team", "away_team", "league", "markets"]
                missing_fields = [field for field in required_fields if field not in prediction]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in prediction: {missing_fields}")
                else:
                    print(f"   ✅ Prediction structure looks good")
                
                # Check markets structure
                markets = prediction.get("markets", {})
                expected_markets = ["ft_win", "ht_win", "ht_over", "ht_ft", "goals", "btts", "asian_handicap", "correct_score", "specials"]
                markets_present = [market for market in expected_markets if market in markets]
                print(f"   🎯 Markets present: {len(markets_present)}/{len(expected_markets)} - {markets_present}")
                
                # Test specific market structures
                if "ft_win" in markets:
                    ft_win = markets["ft_win"]
                    ft_win_fields = ["home_win", "draw", "away_win"]
                    ft_win_valid = all(field in ft_win for field in ft_win_fields)
                    print(f"   ⚽ FT Win market valid: {ft_win_valid}")
                
                if "goals" in markets:
                    goals = markets["goals"]
                    goals_fields = ["over_25", "under_25", "over_15", "under_15"]
                    goals_valid = any(field in goals for field in goals_fields)
                    print(f"   🥅 Goals market valid: {goals_valid}")
        
        # Test market-specific endpoints
        markets_to_test = ["ft_win", "ht_win", "goals", "btts", "asian_handicap"]
        for market in markets_to_test:
            self.run_test(f"Market Predictions - {market}", "GET", f"/predictions/by-market/{market}", 200)

    def test_value_bets_endpoints(self):
        """Test value bets endpoints"""
        print("\n" + "="*50)
        print("TESTING VALUE BETS ENDPOINTS")
        print("="*50)
        
        success, vb_data = self.run_test("Get Value Bets", "GET", "/value-bets?limit=10", 200)
        if success and isinstance(vb_data, dict):
            value_bets = vb_data.get("value_bets", [])
            count = vb_data.get("count", 0)
            total_edge = vb_data.get("total_edge", 0)
            print(f"   ✅ Found {count} value bets with total edge: {total_edge}%")
            
            if value_bets:
                bet = value_bets[0]
                required_fields = ["match_id", "home_team", "away_team", "market", "edge", "odds"]
                missing_fields = [field for field in required_fields if field not in bet]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in value bet: {missing_fields}")
                else:
                    print(f"   ✅ Value bet structure looks good")

        # Test with filters
        self.run_test("Value Bets with Min Edge", "GET", "/value-bets?min_edge=5&limit=5", 200)
        self.run_test("Value Bets High Confidence", "GET", "/value-bets?confidence=high&limit=5", 200)

    def test_leagues_endpoints(self):
        """Test leagues endpoints"""
        print("\n" + "="*50)
        print("TESTING LEAGUES ENDPOINTS")
        print("="*50)
        
        success, leagues_data = self.run_test("Get Leagues", "GET", "/leagues", 200)
        if success and isinstance(leagues_data, dict):
            leagues = leagues_data.get("leagues", [])
            count = leagues_data.get("count", 0)
            print(f"   ✅ Found {count} leagues")
            
            if leagues:
                league = leagues[0]
                required_fields = ["id", "name", "country"]
                missing_fields = [field for field in required_fields if field not in league]
                if missing_fields:
                    print(f"   ⚠️  Missing fields in league: {missing_fields}")
                else:
                    print(f"   ✅ League structure looks good")

    def test_admin_endpoints(self):
        """Test admin endpoints"""
        print("\n" + "="*50)
        print("TESTING ADMIN ENDPOINTS")
        print("="*50)
        
        # Test refresh predictions
        success, refresh_data = self.run_test("Refresh Predictions", "POST", "/admin/refresh-predictions", 200)
        if success:
            message = refresh_data.get("message", "")
            status = refresh_data.get("status", "")
            print(f"   ✅ Refresh triggered: {message} ({status})")

    def run_all_tests(self):
        """Run all API tests"""
        print("🚀 Starting Football Prediction Platform API Tests")
        print(f"📍 Testing against: {self.base_url}")
        
        start_time = datetime.now()
        
        # Run all test suites
        self.test_health_endpoints()
        self.test_dashboard_endpoints()
        self.test_matches_endpoints()
        self.test_predictions_endpoints()  # Main feature
        self.test_value_bets_endpoints()
        self.test_leagues_endpoints()
        self.test_admin_endpoints()
        
        end_time = datetime.now()
        duration = (end_time - start_time).total_seconds()
        
        # Print final results
        print("\n" + "="*60)
        print("FINAL TEST RESULTS")
        print("="*60)
        print(f"📊 Tests passed: {self.tests_passed}/{self.tests_run}")
        print(f"⏱️  Total duration: {duration:.1f} seconds")
        
        if self.failed_tests:
            print(f"\n❌ Failed Tests ({len(self.failed_tests)}):")
            for i, test in enumerate(self.failed_tests, 1):
                print(f"   {i}. {test['test']} - {test['endpoint']}")
                if 'error' in test:
                    print(f"      Error: {test['error']}")
                else:
                    print(f"      Expected: {test['expected']}, Got: {test['actual']}")
        else:
            print("\n🎉 All tests passed!")
        
        return 0 if self.tests_passed == self.tests_run else 1

def main():
    tester = FootballPredictionAPITester()
    return tester.run_all_tests()

if __name__ == "__main__":
    sys.exit(main())