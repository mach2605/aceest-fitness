import pytest
import json
from app import app, workouts

@pytest.fixture
def client():
    """Create a test client for the Flask application"""
    app.config['TESTING'] = True
    app.config['WTF_CSRF_ENABLED'] = False
    
    with app.test_client() as client:
        with app.app_context():
            # Clear workouts before each test
            workouts.clear()
            yield client

@pytest.fixture
def sample_workout_data():
    """Sample workout data for testing"""
    return {
        'workout_name': 'Push-ups',
        'duration': '30'
    }

class TestHomePage:
    """Test cases for the home page"""
    
    def test_home_page_loads(self, client):
        """Test that home page loads successfully"""
        response = client.get('/')
        assert response.status_code == 200
        assert b'ACEest Fitness' in response.data
        assert b'Track Your Workout Journey' in response.data
    
    def test_home_page_contains_form(self, client):
        """Test that home page contains the workout form"""
        response = client.get('/')
        assert b'workout_name' in response.data
        assert b'duration' in response.data
        assert b'Add Workout' in response.data

class TestAddWorkout:
    """Test cases for adding workouts"""
    
    def test_add_valid_workout(self, client, sample_workout_data):
        """Test adding a valid workout"""
        response = client.post('/add_workout', data=sample_workout_data, follow_redirects=True)
        assert response.status_code == 200
        print(response.data)
        assert b"Push-ups added successfully" in response.data
        assert len(workouts) == 1
        assert workouts[0]['workout'] == 'Push-ups'
        assert workouts[0]['duration'] == 30
    
    def test_add_workout_missing_name(self, client):
        """Test adding workout without name"""
        response = client.post('/add_workout', data={
            'workout_name': '',
            'duration': '30'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Workout name is required!' in response.data
        assert len(workouts) == 0
    
    def test_add_workout_missing_duration(self, client):
        """Test adding workout without duration"""
        response = client.post('/add_workout', data={
            'workout_name': 'Running',
            'duration': ''
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Duration is required!' in response.data
        assert len(workouts) == 0
    
    def test_add_workout_invalid_duration_string(self, client):
        """Test adding workout with invalid duration (string)"""
        response = client.post('/add_workout', data={
            'workout_name': 'Swimming',
            'duration': 'thirty'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Duration must be a valid number!' in response.data
        assert len(workouts) == 0
    
    def test_add_workout_negative_duration(self, client):
        """Test adding workout with negative duration"""
        response = client.post('/add_workout', data={
            'workout_name': 'Yoga',
            'duration': '-10'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Duration must be a positive number!' in response.data
        assert len(workouts) == 0
    
    def test_add_workout_zero_duration(self, client):
        """Test adding workout with zero duration"""
        response = client.post('/add_workout', data={
            'workout_name': 'Stretching',
            'duration': '0'
        }, follow_redirects=True)
        assert response.status_code == 200
        assert b'Duration must be a positive number!' in response.data
        assert len(workouts) == 0
    
    def test_add_multiple_workouts(self, client):
        """Test adding multiple workouts"""
        workouts_data = [
            {'workout_name': 'Push-ups', 'duration': '20'},
            {'workout_name': 'Running', 'duration': '45'},
            {'workout_name': 'Squats', 'duration': '15'}
        ]
        
        for workout_data in workouts_data:
            client.post('/add_workout', data=workout_data, follow_redirects=True)
        
        assert len(workouts) == 3
        assert workouts[0]['workout'] == 'Push-ups'
        assert workouts[1]['workout'] == 'Running'
        assert workouts[2]['workout'] == 'Squats'

class TestViewWorkouts:
    """Test cases for viewing workouts"""
    
    def test_view_workouts_empty(self, client):
        """Test viewing workouts when none exist"""
        response = client.get('/workouts')
        assert response.status_code == 200
        assert b'No Workouts Yet!' in response.data
        assert b'Start your fitness journey' in response.data
    
    def test_view_workouts_with_data(self, client, sample_workout_data):
        """Test viewing workouts with existing data"""
        # Add a workout first
        client.post('/add_workout', data=sample_workout_data)
        
        response = client.get('/workouts')
        assert response.status_code == 200
        assert b'Push-ups' in response.data
        assert b'30 minutes' in response.data
        assert b'Your Fitness Stats' in response.data
    
    def test_workout_stats_calculation(self, client):
        """Test that workout statistics are calculated correctly"""
        workouts_data = [
            {'workout_name': 'Running', 'duration': '30'},
            {'workout_name': 'Swimming', 'duration': '45'},
            {'workout_name': 'Cycling', 'duration': '60'}
        ]
        
        for workout_data in workouts_data:
            client.post('/add_workout', data=workout_data)
        
        response = client.get('/workouts')
        assert response.status_code == 200
        # Total workouts: 3
        # Total duration: 135 minutes
        # Average: 45 minutes
        assert b'135' in response.data  # Total minutes
        assert b'45.0' in response.data  # Average duration

class TestAPIEndpoints:
    """Test cases for API endpoints"""
    
    def test_api_get_workouts_empty(self, client):
        """Test API get workouts when empty"""
        response = client.get('/api/workouts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_count'] == 0
        assert len(data['workouts']) == 0
    
    def test_api_get_workouts_with_data(self, client, sample_workout_data):
        """Test API get workouts with existing data"""
        client.post('/add_workout', data=sample_workout_data)
        
        response = client.get('/api/workouts')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert data['total_count'] == 1
        assert len(data['workouts']) == 1
        assert data['workouts'][0]['workout'] == 'Push-ups'
        assert data['workouts'][0]['duration'] == 30
    
    def test_api_add_workout_valid(self, client):
        """Test API add workout with valid data"""
        workout_data = {
            'workout_name': 'Deadlifts',
            'duration': 40
        }
        
        response = client.post('/api/workouts', 
                             data=json.dumps(workout_data),
                             content_type='application/json')
        assert response.status_code == 201
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'Deadlifts' in data['message']
        assert data['workout']['workout'] == 'Deadlifts'
        assert data['workout']['duration'] == 40
    
    def test_api_add_workout_missing_name(self, client):
        """Test API add workout without name"""
        workout_data = {
            'duration': 30
        }
        
        response = client.post('/api/workouts', 
                             data=json.dumps(workout_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Workout name is required' in data['error']
    
    def test_api_add_workout_invalid_duration(self, client):
        """Test API add workout with invalid duration"""
        workout_data = {
            'workout_name': 'Bench Press',
            'duration': 'invalid'
        }
        
        response = client.post('/api/workouts', 
                             data=json.dumps(workout_data),
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Duration must be a valid number' in data['error']
    
    def test_api_add_workout_no_data(self, client):
        """Test API add workout without data"""
        response = client.post('/api/workouts', 
                             data='',
                             content_type='application/json')
        assert response.status_code == 400
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'No data provided' in data['error']
    
    def test_api_delete_workout(self, client, sample_workout_data):
        """Test API delete workout"""
        # First add a workout
        client.post('/add_workout', data=sample_workout_data)
        workout_id = workouts[0]['id']
        
        response = client.delete(f'/api/workouts/{workout_id}')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['success'] is True
        assert 'deleted successfully' in data['message']
        assert len(workouts) == 0
    
    def test_api_delete_nonexistent_workout(self, client):
        """Test API delete nonexistent workout"""
        response = client.delete('/api/workouts/999')
        assert response.status_code == 404
        data = json.loads(response.data)
        assert data['success'] is False
        assert 'Workout not found' in data['error']

class TestHealthCheck:
    """Test cases for health check endpoint"""
    
    def test_health_check(self, client):
        """Test health check endpoint"""
        response = client.get('/health')
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data['status'] == 'healthy'
        assert data['service'] == 'ACEest Fitness Tracker'
        assert 'timestamp' in data
        assert 'total_workouts' in data

class TestErrorHandlers:
    """Test cases for error handlers"""
    
    def test_404_error(self, client):
        """Test 404 error handler"""
        response = client.get('/nonexistent-page')
        assert response.status_code == 404
    

class TestWorkoutDataStructure:
    """Test cases for workout data structure and integrity"""
    
    def test_workout_id_incrementation(self, client):
        """Test that workout IDs increment properly"""
        workout_data = [
            {'workout_name': 'Exercise 1', 'duration': '10'},
            {'workout_name': 'Exercise 2', 'duration': '20'},
            {'workout_name': 'Exercise 3', 'duration': '30'}
        ]
        
        for data in workout_data:
            client.post('/add_workout', data=data)
        
        assert workouts[0]['id'] == 1
        assert workouts[1]['id'] == 2
        assert workouts[2]['id'] == 3
    
    def test_workout_contains_timestamp(self, client, sample_workout_data):
        """Test that workouts contain timestamp"""
        client.post('/add_workout', data=sample_workout_data)
        
        assert 'date_added' in workouts[0]
        assert workouts[0]['date_added'] is not None
        # Check that timestamp format is reasonable (contains year, month, day)
        timestamp = workouts[0]['date_added']
        assert '2024' in timestamp or '2025' in timestamp
        assert ':' in timestamp  # Should contain time
    
    def test_workout_data_types(self, client, sample_workout_data):
        """Test that workout data has correct types"""
        client.post('/add_workout', data=sample_workout_data)
        
        workout = workouts[0]
        assert isinstance(workout['id'], int)
        assert isinstance(workout['workout'], str)
        assert isinstance(workout['duration'], int)
        assert isinstance(workout['date_added'], str)