import pytest
from processor.performance import analyze_performance

def test_analyze_performance_google():
	result = analyze_performance('https://www.google.com')
	assert isinstance(result, dict)
	assert 'load_time_ms' in result
	assert 'total_size_kb' in result
	assert result['load_time_ms'] > 0
	assert result['total_size_kb'] > 0
