from datetime import date
from functools import wraps


def daily_rate_limit(max_calls, session, model):
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            today = date.today().strftime("%Y-%m-%d")
            task_name = func.__name__
            with session.begin():
                usage_stat = (
                    session.query(model)
                    .filter(model.task_name == task_name, model.day == today)
                    .first()
                )
                if usage_stat:
                    if usage_stat.count >= max_calls:
                        raise Exception(
                            f"Rate limit exceeded for {task_name} on {today}"
                        )
                    usage_stat.count += 1
                else:
                    usage_stat = model(task_name=task_name, day=today, count=1)
                    session.add(usage_stat)
            return func(*args, **kwargs)

        return wrapper

    return decorator
