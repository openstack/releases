import os
import os.path

# Try to guess where the deliverables directory is relative to where
# the code is imported from.
_venv = os.environ.get('VIRTUAL_ENV', '')
if _venv:
    deliverable_dir = os.path.dirname(_venv)
    if deliverable_dir.endswith('.tox'):
        deliverable_dir = os.path.dirname(deliverable_dir)
    deliverable_dir = os.path.join(deliverable_dir, 'deliverables')
else:
    deliverable_dir = os.path.join(
        os.path.dirname(__file__),
        '../deliverables',
    )
