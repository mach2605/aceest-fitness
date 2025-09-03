from flask import Flask, render_template, flash, redirect, url_for, request, jsonify
from datetime import datetime
import json

app = Flask(__name__)
app.secret_key = 'session-secret-key'  # Needed for flash messages

# In-memory storage for workouts 
workouts = []

@app.route("/")
def index():
    return render_template('index.html', workouts=workouts)

@app.route('/add_workout', methods=['POST'])
def add_workout():
    """Add a new workout"""
    try:
        workout_name = request.form.get('workout_name', '').strip()
        duration = request.form.get('duration', '').strip()
        
        # Validation
        if not workout_name:
            flash('Workout name is required!', 'error')
            return redirect(url_for('index'))
        
        if not duration:
            flash('Duration is required!', 'error')
            return redirect(url_for('index'))
        
        try:
            duration_int = int(duration)
            if duration_int <= 0:
                flash('Duration must be a positive number!', 'error')
                return redirect(url_for('index'))
        except ValueError:
            flash('Duration must be a valid number!', 'error')
            return redirect(url_for('index'))
        
        # Add workout to storage
        new_workout = {
            'id': len(workouts) + 1,
            'workout': workout_name,
            'duration': duration_int,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        workouts.append(new_workout)
        flash(f"{workout_name} added successfully!", 'success')
        
    except Exception as e:
        flash(f'An error occurred: {str(e)}', 'error')
    
    return redirect(url_for('index'))

@app.route('/workouts')
def view_workouts():
    """View all logged workouts"""
    return render_template('workouts.html', workouts=workouts)

@app.route('/api/workouts', methods=['GET'])
def api_get_workouts():
    """API endpoint to get all workouts as JSON"""
    return jsonify({
        'success': True,
        'workouts': workouts,
        'total_count': len(workouts)
    })

@app.route('/api/workouts', methods=['POST'])
def api_add_workout():
    """API endpoint to add workout via JSON"""
    try:
        data = request.get_json(silent=True)
        if not data:
            return jsonify({'success': False, 'error': 'No data provided'}), 400

        workout_name = data.get('workout_name', '').strip()
        duration = data.get('duration')

        if not workout_name:
            return jsonify({'success': False, 'error': 'Workout name is required'}), 400

        if not duration:
            return jsonify({'success': False, 'error': 'Duration is required'}), 400

        try:
            duration_int = int(duration)
            if duration_int <= 0:
                return jsonify({'success': False, 'error': 'Duration must be positive'}), 400
        except (ValueError, TypeError):
            return jsonify({'success': False, 'error': 'Duration must be a valid number'}), 400

        new_workout = {
            'id': len(workouts) + 1,
            'workout': workout_name,
            'duration': duration_int,
            'date_added': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }

        workouts.append(new_workout)

        return jsonify({
            'success': True,
            'message': f"{workout_name} added successfully!",
            'workout': new_workout
        }), 201

    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/workouts/<int:workout_id>', methods=['DELETE'])
def api_delete_workout(workout_id):
    """API endpoint to delete a workout"""
    workout_to_remove = None
    
    for workout in workouts:
        if workout['id'] == workout_id:
            workout_to_remove = workout
            break
    
    if workout_to_remove:
        workouts.remove(workout_to_remove)
        return jsonify({
            'success': True,
            'message': f"Workout '{workout_to_remove['workout']}' deleted successfully!"
        })
    else:
        return jsonify({'success': False, 'error': 'Workout not found'}), 404

@app.route('/health')
def health_check():
    """Health check endpoint for monitoring"""
    return jsonify({
        'status': 'healthy',
        'service': 'ACEest Fitness Tracker',
        'timestamp': datetime.now().isoformat(),
        'total_workouts': len(workouts)
    })

@app.errorhandler(404)
def not_found(error):
    return "<p>Not Found</p>", 404

@app.errorhandler(500)
def internal_error(error):
    return "<p>Server Error</p>", 500

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)