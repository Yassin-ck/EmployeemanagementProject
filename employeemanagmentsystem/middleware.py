from django.utils import timezone
from accounts.models import User, FailedLoginAttempt

class BlockUserAfterFailedAttemptsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.method == 'POST' and 'username' in request.POST and 'password' in request.POST:
            login_url = '/'
            if request.path == login_url:
                username = request.POST['username']
                password = request.POST['password']
                user = User.objects.filter(username=username).first()
                if user is not None and not user.check_password(password):
                    try:
                        failed_attempt = FailedLoginAttempt.objects.get(user=user)
                        failed_attempt.attempt_count += 1
                        failed_attempt.last_attempt_time = timezone.now()
                        failed_attempt.save()
                        if failed_attempt.attempt_count >= failed_attempt.block_after_attempts:
                            user.is_active = False
                            user.save()
                            failed_attempt.save()
                    except FailedLoginAttempt.DoesNotExist:
                        FailedLoginAttempt.objects.create(user=user, attempt_count=1, last_attempt_time=timezone.now())

        # Handle GET requests - return the original response
        response = self.get_response(request)
        return response
