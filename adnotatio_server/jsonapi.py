import json
import traceback

import decorator
from flask import current_app, Response


def jsonapify(data=None, errors=None):
    if data is None and errors is None:
        raise RuntimeError("Either data or errors MUST be provided.")
    if data is not None and errors is not None:
        raise RuntimeError("You cannot specify both data and errors.")

    if data is not None:
        content = {'data': data}
        status = 200
    else:
        content = {'errors': errors}
        status = 500

    return Response(
        json.dumps(content),
        status=status,
        mimetype='application/vnd.api+json'
    )


@decorator.decorator
def jsonapify_wrap(f, *args, **kwargs):
    try:
        return jsonapify(data=f(*args, **kwargs))
    except Exception as e:
        return jsonapify(errors=[
            {'title': str(e), 'detail': traceback.format_exc()}
            if current_app.config['DEBUG'] else
            {'title': 'Something went wrong!'}
        ])
