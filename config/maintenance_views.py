from django.http import JsonResponse
from django.core.management import call_command
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
import io
import sys

@csrf_exempt
def reset_database_view(request):
    """
    View to flush the database. 
    WARNING: This deletes all data!
    Requires a secret query param 'key' to match a predefined secret.
    """
    # Security check: Simple query param check
    # In production, use a strong secret or environment variable.
    # User must access: /api/maintenance/reset-db/?key=SUPER_SECRET_KEY
    
    secret_key = request.GET.get('key')
    
    # You can change 'SUPER_SECRET_KEY' to something else if you prefer
    if secret_key != 'SUPER_SECRET_KEY':
        return JsonResponse({'error': 'Unauthorized. Invalid key.'}, status=403)

    try:
        # Capture stdout to show the output
        out = io.StringIO()
        
        # Run the flush command
        # interactive=False prevents it from asking "Are you sure?"
        call_command('flush', interactive=False, stdout=out)
        
        return JsonResponse({
            'status': 'success',
            'message': 'Database flushed successfully.',
            'output': out.getvalue()
        })
    except Exception as e:
        return JsonResponse({
            'status': 'error',
            'message': str(e)
        }, status=500)
