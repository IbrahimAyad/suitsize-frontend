"""
Railway Backend Integration for ML-Enhanced SuitSize Engine
Replaces the current Flask API with ML-powered recommendations
"""

import sys
import os
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ml_enhanced_sizing_engine import EnhancedSuitSizeEngine

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class MLEnhancedRailwayBackend:
    """ML-Enhanced Railway Backend with improved error handling and caching"""
    
    def __init__(self):
        # Initialize the ML engine
        self.ml_engine = EnhancedSuitSizeEngine()
        
        # Simple in-memory cache (in production, use Redis)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes
        
        # Rate limiting (in production, use Redis)
        self.request_counts = {}
        self.rate_limit = 10  # 10 requests per minute
        
        logger.info("🚀 ML-Enhanced Railway Backend initialized")
    
    def get_cache_key(self, height: float, weight: float, fit: str, unit: str = 'metric') -> str:
        """Generate cache key for request"""
        return f"{height:.1f}_{weight:.1f}_{fit}_{unit}"
    
    def is_cache_valid(self, cache_entry: Dict[str, Any]) -> bool:
        """Check if cache entry is still valid"""
        timestamp = cache_entry.get('timestamp')
        if isinstance(timestamp, str):
            # Handle ISO timestamp format
            try:
                timestamp = datetime.fromisoformat(timestamp.replace('Z', '+00:00')).timestamp()
            except:
                return False
        elif isinstance(timestamp, datetime):
            timestamp = timestamp.timestamp()
        elif not isinstance(timestamp, (int, float)):
            return False
        
        return time.time() - timestamp < self.cache_ttl
    
    def check_rate_limit(self, client_ip: str) -> bool:
        """Check if client is within rate limits"""
        current_time = time.time()
        minute_window = int(current_time // 60)
        
        if client_ip not in self.request_counts:
            self.request_counts[client_ip] = {}
        
        # Clean old entries
        keys_to_remove = [k for k in self.request_counts[client_ip].keys() 
                         if k < minute_window - 1]
        for key in keys_to_remove:
            del self.request_counts[client_ip][key]
        
        # Check current minute
        current_count = self.request_counts[client_ip].get(minute_window, 0)
        
        if current_count >= self.rate_limit:
            return False
        
        # Increment count
        self.request_counts[client_ip][minute_window] = current_count + 1
        return True
    
    def validate_input(self, data: Dict[str, Any]) -> tuple[bool, str, Dict[str, Any]]:
        """Validate input data and convert units if needed"""
        
        try:
            # Extract and validate required fields
            height = data.get('height')
            weight = data.get('weight')
            fit = data.get('fit', 'regular')
            unit = data.get('unit', 'metric')
            
            # Validate height
            if height is None:
                return False, "Height is required", {}
            
            try:
                height = float(height)
            except (ValueError, TypeError):
                return False, "Height must be a valid number", {}
            
            # Validate weight
            if weight is None:
                return False, "Weight is required", {}
            
            try:
                weight = float(weight)
            except (ValueError, TypeError):
                return False, "Weight must be a valid number", {}
            
            # Validate fit preference
            valid_fits = ['slim', 'regular', 'relaxed']
            if fit not in valid_fits:
                return False, f"Fit must be one of: {', '.join(valid_fits)}", {}
            
            # Validate unit
            valid_units = ['metric', 'imperial']
            if unit not in valid_units:
                return False, f"Unit must be one of: {', '.join(valid_units)}", {}
            
            # Validate realistic ranges (expanded from original)
            if height < 120 or height > 250:
                return False, "Height must be between 120cm and 250cm", {}
            
            if weight < 40 or weight > 200:
                return False, "Weight must be between 40kg and 200kg", {}
            
            return True, "", {
                'height': height,
                'weight': weight,
                'fit': fit,
                'unit': unit
            }
            
        except Exception as e:
            return False, f"Validation error: {str(e)}", {}
    
    def process_sizing_request(self, request_data: Dict[str, Any], client_ip: str = "127.0.0.1") -> Dict[str, Any]:
        """Process sizing request with ML enhancement"""
        
        start_time = time.time()
        
        # Check rate limiting
        if not self.check_rate_limit(client_ip):
            return {
                'error': 'Rate limit exceeded. Maximum 10 requests per minute.',
                'retry_after': 60,
                'timestamp': datetime.now().isoformat()
            }
        
        # Validate input
        is_valid, error_message, validated_data = self.validate_input(request_data)
        if not is_valid:
            return {
                'error': error_message,
                'code': 'VALIDATION_ERROR',
                'timestamp': datetime.now().isoformat()
            }
        
        # Check cache
        cache_key = self.get_cache_key(**validated_data)
        if cache_key in self.cache and self.is_cache_valid(self.cache[cache_key]):
            cached_result = self.cache[cache_key].copy()
            cached_result['cached'] = True
            cached_result['processing_time_ms'] = round((time.time() - start_time) * 1000, 1)
            logger.info(f"📋 Cache hit for {cache_key}")
            return cached_result
        
        # Get ML-enhanced recommendation
        try:
            ml_result = self.ml_engine.get_size_recommendation(**validated_data)
            
            # Format response for API
            api_response = {
                'size': ml_result['size'],
                'confidence': round(ml_result['confidence'], 3),
                'confidenceLevel': ml_result['confidenceLevel'],
                'bodyType': ml_result['bodyType'],
                'rationale': ml_result['rationale'],
                'alterations': ml_result['alterations'],
                'measurements': ml_result['measurements'],
                'cached': False,
                'timestamp': datetime.now().isoformat(),
                'processing_time_ms': round((time.time() - start_time) * 1000, 1),
                'engine_version': ml_result.get('mlModel', 'ML-Enhanced v2.0'),
                'similar_customers_found': ml_result.get('similarCustomers', 0),
                'anthropometric_analysis': {
                    'bmi': ml_result['measurements']['bmi'],
                    'percentiles': ml_result.get('percentiles', {}),
                    'validation_notes': ml_result.get('validationNotes', [])
                }
            }
            
            # Add confidence warnings
            if ml_result['confidence'] < 0.6:
                api_response['warning'] = "Low confidence recommendation - consider manual fitting"
            elif ml_result['confidence'] < 0.75:
                api_response['notice'] = "Medium confidence recommendation - alterations may be needed"
            
            # Cache the result
            api_response['timestamp'] = datetime.now().isoformat()
            self.cache[cache_key] = api_response.copy()
            
            logger.info(f"✅ ML recommendation: {ml_result['size']} "
                       f"(confidence: {ml_result['confidence']:.1%}, "
                       f"time: {api_response['processing_time_ms']}ms)")
            
            return api_response
            
        except Exception as e:
            logger.error(f"❌ ML Engine error: {str(e)}")
            return {
                'error': 'Internal processing error',
                'code': 'INTERNAL_ERROR',
                'details': str(e) if os.getenv('FLASK_ENV') == 'development' else 'Please try again',
                'timestamp': datetime.now().isoformat()
            }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get health status of the ML engine"""
        
        try:
            # Test ML engine with sample data
            test_result = self.ml_engine.get_size_recommendation(height=175, weight=75, fit='regular')
            
            engine_stats = self.ml_engine.get_engine_stats()
            
            return {
                'status': 'healthy',
                'timestamp': datetime.now().isoformat(),
                'engine_version': engine_stats['version'],
                'ml_models_loaded': engine_stats['mlModelsTrained'],
                'customer_database_size': engine_stats['customerDatabaseSize'],
                'test_prediction': {
                    'size': test_result['size'],
                    'confidence': round(test_result['confidence'], 3)
                },
                'cache_size': len(self.cache),
                'rate_limit_active': True
            }
            
        except Exception as e:
            logger.error(f"❌ Health check failed: {str(e)}")
            return {
                'status': 'unhealthy',
                'error': str(e),
                'timestamp': datetime.now().isoformat()
            }
    
    def get_stats(self) -> Dict[str, Any]:
        """Get system statistics"""
        
        engine_stats = self.ml_engine.get_engine_stats()
        
        return {
            'engine_stats': engine_stats,
            'cache_info': {
                'size': len(self.cache),
                'ttl_seconds': self.cache_ttl
            },
            'rate_limiting': {
                'requests_per_minute': self.rate_limit,
                'active_clients': len(self.request_counts)
            },
            'timestamp': datetime.now().isoformat()
        }
    
    def clear_cache(self) -> Dict[str, Any]:
        """Clear the recommendation cache"""
        
        cache_size = len(self.cache)
        self.cache.clear()
        
        logger.info(f"🧹 Cache cleared ({cache_size} entries removed)")
        
        return {
            'message': f'Cache cleared successfully',
            'entries_removed': cache_size,
            'timestamp': datetime.now().isoformat()
        }

# Flask application (for Railway deployment)
try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    
    app = Flask(__name__)
    CORS(app)  # Enable CORS for web integration
    
    # Initialize the ML-enhanced backend
    ml_backend = MLEnhancedRailwayBackend()
    
    @app.route('/api/health', methods=['GET'])
    def health_check():
        """Health check endpoint"""
        return jsonify(ml_backend.get_health_status())
    
    @app.route('/api/recommend', methods=['POST'])
    def recommend_size():
        """Main sizing recommendation endpoint"""
        
        try:
            # Get client IP for rate limiting
            client_ip = request.headers.get('X-Forwarded-For', request.remote_addr)
            
            # Get request data
            if request.is_json:
                data = request.get_json()
            else:
                data = request.form.to_dict()
            
            # Process request
            result = ml_backend.process_sizing_request(data, client_ip)
            
            # Return appropriate HTTP status code
            if 'error' in result:
                return jsonify(result), 400
            else:
                return jsonify(result)
                
        except Exception as e:
            logger.error(f"❌ API error: {str(e)}")
            return jsonify({
                'error': 'Internal server error',
                'code': 'SERVER_ERROR',
                'timestamp': datetime.now().isoformat()
            }), 500
    
    @app.route('/api/stats', methods=['GET'])
    def get_stats():
        """Get system statistics"""
        return jsonify(ml_backend.get_stats())
    
    @app.route('/api/cache/clear', methods=['POST'])
    def clear_cache():
        """Clear recommendation cache"""
        return jsonify(ml_backend.clear_cache())
    
    @app.route('/', methods=['GET'])
    def root():
        """Root endpoint with API information"""
        return jsonify({
            'message': 'ML-Enhanced SuitSize API v2.0',
            'version': '2.0-ML-Enhanced',
            'endpoints': {
                'health': '/api/health',
                'recommend': '/api/recommend (POST)',
                'stats': '/api/stats',
                'cache_clear': '/api/cache/clear (POST)'
            },
            'timestamp': datetime.now().isoformat()
        })

except ImportError:
    logger.warning("Flask not available - running in standalone mode")
    app = None

# Command-line interface for testing
def cli_main():
    """Command-line interface for testing"""
    
    print("🤖 ML-Enhanced SuitSize CLI")
    print("=" * 40)
    
    backend = MLEnhancedRailwayBackend()
    
    while True:
        print("\nOptions:")
        print("1. Test sizing recommendation")
        print("2. Health check")
        print("3. System stats")
        print("4. Clear cache")
        print("5. Exit")
        
        choice = input("\nEnter choice (1-5): ").strip()
        
        if choice == '1':
            try:
                height = float(input("Height: "))
                weight = float(input("Weight: "))
                fit = input("Fit (slim/regular/relaxed) [regular]: ").strip() or 'regular'
                unit = input("Unit (metric/imperial) [metric]: ").strip() or 'metric'
                
                result = backend.process_sizing_request({
                    'height': height,
                    'weight': weight,
                    'fit': fit,
                    'unit': unit
                })
                
                print("\n📋 Recommendation:")
                print(json.dumps(result, indent=2))
                
            except (ValueError, KeyboardInterrupt):
                print("\n❌ Invalid input or cancelled")
        
        elif choice == '2':
            print("\n🏥 Health Check:")
            print(json.dumps(backend.get_health_status(), indent=2))
        
        elif choice == '3':
            print("\n📊 System Stats:")
            print(json.dumps(backend.get_stats(), indent=2))
        
        elif choice == '4':
            print("\n🧹 Cache cleared:")
            print(json.dumps(backend.clear_cache(), indent=2))
        
        elif choice == '5':
            print("👋 Goodbye!")
            break
        
        else:
            print("❌ Invalid choice")

if __name__ == '__main__':
    if app:
        # Run Flask app
        port = int(os.environ.get('PORT', 5000))
        logger.info(f"🚀 Starting Flask app on port {port}")
        app.run(host='0.0.0.0', port=port, debug=False)
    else:
        # Run CLI
        cli_main()